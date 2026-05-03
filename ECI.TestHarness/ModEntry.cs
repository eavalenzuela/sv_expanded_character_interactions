using System.Text;
using StardewModdingAPI;
using StardewValley;

namespace ECI.TestHarness;

// ---------- scenario-file schema ----------
// JSON file is a flat list of scenario objects, e.g.
//   [{"Name":"...", "Setup":{"Time":1900}, "Assert":{"Npc":"Linus", "TextContains":"sentinel"}}]

public class Scenario
{
    public string Name { get; set; } = "";
    public ScenarioSetup? Setup { get; set; }
    public ScenarioAssert Assert { get; set; } = new();
}

public class ScenarioSetup
{
    public int? Time { get; set; }                 // 600..2600 (Stardew HHMM)
    public string? Weather { get; set; }           // Sun | Rain | Storm | Snow | Wind
    public Dictionary<string, int>? Hearts { get; set; }   // NPC -> hearts
    public string? WarpPlayerTo { get; set; }      // location internal name
}

public class ScenarioAssert
{
    public string Npc { get; set; } = "";
    public string? TextContains { get; set; }
    public string? TextEquals { get; set; }
}

/// <summary>Diagnostic console commands for inspecting ECI dialogue
/// patches at runtime. Three commands:
///
///   eci_dump &lt;NPC&gt;
///       Loads Characters/Dialogue/&lt;NPC&gt; from the live content
///       pipeline (i.e., post-CP-patches) and prints every key + value.
///       Tells you whether the asset CP is supposed to have modified
///       actually contains your overrides at the moment of inspection.
///
///   eci_npcdialogue &lt;NPC&gt;
///       Prints the in-memory NPC instance's CurrentDialogue stack and
///       the dialogue dictionary it loaded for today. If this differs
///       from `eci_dump`, the NPC has stale cached dialogue from before
///       CP applied — the runtime cache bug class.
///
///   eci_state
///       Dumps the current world context: date, time, weather, player
///       location, friendship hearts. Useful for confirming that
///       `patch summary` and your test scenarios are running against
///       the same conditions.
/// </summary>
public class ModEntry : Mod
{
    public override void Entry(IModHelper helper)
    {
        helper.ConsoleCommands.Add(
            "eci_dump",
            "Print the live Characters/Dialogue/<NPC> dict (post-CP). Usage: eci_dump <NPC>",
            this.OnDump);

        helper.ConsoleCommands.Add(
            "eci_npcdialogue",
            "Print the NPC's in-memory dialogue state. Usage: eci_npcdialogue <NPC>",
            this.OnNpcDialogue);

        helper.ConsoleCommands.Add(
            "eci_state",
            "Print the current world / player context relevant to dialogue selection.",
            this.OnState);

        helper.ConsoleCommands.Add(
            "eci_settime",
            "Set Game1.timeOfDay. Usage: eci_settime <HHMM>",
            this.OnSetTime);

        helper.ConsoleCommands.Add(
            "eci_setfriendship",
            "Set friendship hearts for an NPC. Usage: eci_setfriendship <NPC> <hearts>",
            this.OnSetFriendship);

        helper.ConsoleCommands.Add(
            "eci_runfile",
            "Run a JSON scenario file under Mods/ECI.TestHarness/. Usage: eci_runfile <relative_path>",
            this.OnRunFile);
    }

    // ---------- eci_dump ----------

    private void OnDump(string command, string[] args)
    {
        if (args.Length < 1)
        {
            this.Monitor.Log("Usage: eci_dump <NPC>", LogLevel.Error);
            return;
        }
        string npc = args[0];
        string assetName = $"Characters/Dialogue/{npc}";

        Dictionary<string, string>? dialogue;
        try
        {
            dialogue = this.Helper.GameContent.Load<Dictionary<string, string>>(assetName);
        }
        catch (Exception ex)
        {
            this.Monitor.Log($"Failed to load {assetName}: {ex.Message}", LogLevel.Error);
            return;
        }

        if (dialogue == null || dialogue.Count == 0)
        {
            this.Monitor.Log($"{assetName}: empty / not found.", LogLevel.Warn);
            return;
        }

        var sb = new StringBuilder();
        sb.AppendLine($"=== {assetName} ({dialogue.Count} entries; live content-pipeline view) ===");
        foreach (var (k, v) in dialogue.OrderBy(kv => kv.Key, StringComparer.Ordinal))
        {
            string preview = v.Replace("\n", " ").Replace("\r", "");
            if (preview.Length > 160) preview = preview.Substring(0, 160) + "…";
            sb.AppendLine($"  {k,-32} | {preview}");
        }
        this.Monitor.Log(sb.ToString(), LogLevel.Info);
    }

    // ---------- eci_npcdialogue ----------

    private void OnNpcDialogue(string command, string[] args)
    {
        if (args.Length < 1)
        {
            this.Monitor.Log("Usage: eci_npcdialogue <NPC>", LogLevel.Error);
            return;
        }
        if (!Context.IsWorldReady)
        {
            this.Monitor.Log("World not ready (no save loaded).", LogLevel.Warn);
            return;
        }

        string name = args[0];
        NPC? npc = Game1.getCharacterFromName(name);
        if (npc == null)
        {
            this.Monitor.Log($"NPC '{name}' not found in the loaded save.", LogLevel.Warn);
            return;
        }

        var sb = new StringBuilder();
        sb.AppendLine($"=== {name} — in-memory NPC dialogue state ===");
        sb.AppendLine($"  Location: {npc.currentLocation?.Name ?? "<null>"}  "
                      + $"Tile: ({npc.Tile.X}, {npc.Tile.Y})");
        sb.AppendLine($"  Hearts (player): {Game1.player.getFriendshipHeartLevelForNPC(name)}");
        sb.AppendLine($"  CurrentDialogue stack: {npc.CurrentDialogue.Count} entries");

        int idx = 0;
        foreach (var d in npc.CurrentDialogue)
        {
            string text = d.getCurrentDialogue() ?? "<empty>";
            string preview = text.Replace("\n", " ").Replace("\r", "");
            if (preview.Length > 160) preview = preview.Substring(0, 160) + "…";
            sb.AppendLine($"    [{idx}] {preview}");
            idx++;
        }

        // Game1.npcDialogues is a per-NPC dialogue dictionary cached at
        // day-start. Inspect ours via the public Dialogue map keyed off
        // the NPC's `Dialogue` field if available.
        try
        {
            var field = typeof(NPC).GetField("Dialogue",
                System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
            if (field?.GetValue(npc) is Dictionary<string, string> daily)
            {
                sb.AppendLine($"  NPC.Dialogue dict: {daily.Count} entries");
                foreach (var (k, v) in daily.OrderBy(kv => kv.Key, StringComparer.Ordinal).Take(20))
                {
                    string preview = v.Replace("\n", " ").Replace("\r", "");
                    if (preview.Length > 100) preview = preview.Substring(0, 100) + "…";
                    sb.AppendLine($"    {k,-24} | {preview}");
                }
                if (daily.Count > 20)
                    sb.AppendLine($"    … and {daily.Count - 20} more");
            }
            else
            {
                sb.AppendLine("  NPC.Dialogue dict: <not found via reflection>");
            }
        }
        catch (Exception ex)
        {
            sb.AppendLine($"  NPC.Dialogue introspection failed: {ex.Message}");
        }

        this.Monitor.Log(sb.ToString(), LogLevel.Info);
    }

    // ---------- eci_state ----------

    private void OnState(string command, string[] args)
    {
        if (!Context.IsWorldReady)
        {
            this.Monitor.Log("World not ready (no save loaded).", LogLevel.Warn);
            return;
        }

        var p = Game1.player;
        string season = Game1.season.ToString().ToLowerInvariant();
        string weekday = Game1.shortDayNameFromDayOfSeason(Game1.dayOfMonth);
        string location = p.currentLocation?.Name ?? "<null>";
        string weather = Game1.IsRainingHere() ? "Rain"
                       : Game1.IsSnowingHere() ? "Snow"
                       : Game1.isLightning ? "Storm"
                       : Game1.IsGreenRainingHere() ? "GreenRain"
                       : Game1.isDebrisWeather ? "Wind"
                       : "Sun";

        var sb = new StringBuilder();
        sb.AppendLine("=== ECI test harness — world state ===");
        sb.AppendLine($"  Year/Season/Day: {Game1.year} / {season} / {Game1.dayOfMonth} ({weekday})");
        sb.AppendLine($"  Time:            {Game1.timeOfDay}");
        sb.AppendLine($"  Weather:         {weather}");
        sb.AppendLine($"  Player:          {p.Name}  Location={location}  Tile=({p.Tile.X},{p.Tile.Y})");
        sb.AppendLine($"  Hearts:");
        foreach (var (name, friendship) in p.friendshipData.Pairs.OrderBy(kv => kv.Key, StringComparer.Ordinal))
        {
            int hearts = friendship.Points / 250;
            sb.AppendLine($"    {name,-16} {hearts} hearts ({friendship.Points} pts) status={friendship.Status}");
        }

        this.Monitor.Log(sb.ToString(), LogLevel.Info);
    }

    // ---------- eci_settime ----------

    private void OnSetTime(string command, string[] args)
    {
        if (args.Length < 1 || !int.TryParse(args[0], out int t))
        {
            this.Monitor.Log("Usage: eci_settime <HHMM>  (e.g. eci_settime 1900)", LogLevel.Error);
            return;
        }
        if (!Context.IsWorldReady)
        {
            this.Monitor.Log("World not ready.", LogLevel.Warn);
            return;
        }
        Game1.timeOfDay = t;
        this.Monitor.Log($"Set timeOfDay to {t}.", LogLevel.Info);
    }

    // ---------- eci_setfriendship ----------

    private void OnSetFriendship(string command, string[] args)
    {
        if (args.Length < 2 || !int.TryParse(args[1], out int hearts))
        {
            this.Monitor.Log("Usage: eci_setfriendship <NPC> <hearts>", LogLevel.Error);
            return;
        }
        if (!Context.IsWorldReady)
        {
            this.Monitor.Log("World not ready.", LogLevel.Warn);
            return;
        }
        string npc = args[0];
        if (!Game1.player.friendshipData.ContainsKey(npc))
            Game1.player.friendshipData[npc] = new StardewValley.Friendship();
        Game1.player.friendshipData[npc].Points = hearts * 250;
        this.Monitor.Log($"Set {npc} friendship to {hearts} hearts ({hearts * 250} pts).", LogLevel.Info);
    }

    // ---------- eci_runfile ----------

    private void OnRunFile(string command, string[] args)
    {
        if (args.Length < 1)
        {
            this.Monitor.Log("Usage: eci_runfile <relative_path>  (path is under Mods/ECI.TestHarness/)", LogLevel.Error);
            return;
        }
        if (!Context.IsWorldReady)
        {
            this.Monitor.Log("World not ready (no save loaded).", LogLevel.Warn);
            return;
        }

        List<Scenario>? scenarios;
        try
        {
            scenarios = this.Helper.Data.ReadJsonFile<List<Scenario>>(args[0]);
        }
        catch (Exception ex)
        {
            this.Monitor.Log($"Failed to read scenarios file '{args[0]}': {ex.Message}", LogLevel.Error);
            return;
        }
        if (scenarios == null || scenarios.Count == 0)
        {
            this.Monitor.Log($"No scenarios in '{args[0]}'.", LogLevel.Warn);
            return;
        }

        int passed = 0;
        int failed = 0;
        foreach (var sc in scenarios)
        {
            try
            {
                ApplySetup(sc.Setup);
                bool ok = AssertScenario(sc.Assert, out string detail);
                if (ok)
                {
                    this.Monitor.Log($"✓ {sc.Name}", LogLevel.Info);
                    passed++;
                }
                else
                {
                    this.Monitor.Log($"✗ {sc.Name} — {detail}", LogLevel.Error);
                    failed++;
                }
            }
            catch (Exception ex)
            {
                this.Monitor.Log($"✗ {sc.Name} — exception: {ex.Message}", LogLevel.Error);
                failed++;
            }
        }
        this.Monitor.Log($"Summary: {passed}/{passed + failed} passed.", LogLevel.Info);
    }

    private void ApplySetup(ScenarioSetup? setup)
    {
        if (setup == null) return;
        if (setup.Time.HasValue) Game1.timeOfDay = setup.Time.Value;
        if (setup.Hearts != null)
        {
            foreach (var (npc, hearts) in setup.Hearts)
            {
                if (!Game1.player.friendshipData.ContainsKey(npc))
                    Game1.player.friendshipData[npc] = new StardewValley.Friendship();
                Game1.player.friendshipData[npc].Points = hearts * 250;
            }
        }
        if (!string.IsNullOrEmpty(setup.WarpPlayerTo))
        {
            Game1.warpFarmer(setup.WarpPlayerTo, 0, 0, false);
        }
        // Weather changes mid-day are noisy; skipped for v1. Use vanilla
        // `debug weather` / sleep cycle for weather scenarios.
    }

    private bool AssertScenario(ScenarioAssert a, out string detail)
    {
        detail = "";
        if (string.IsNullOrEmpty(a.Npc))
        {
            detail = "scenario missing 'npc'";
            return false;
        }
        NPC? npc = Game1.getCharacterFromName(a.Npc);
        if (npc == null)
        {
            detail = $"NPC '{a.Npc}' not found";
            return false;
        }
        if (npc.CurrentDialogue.Count == 0)
        {
            detail = $"{a.Npc}.CurrentDialogue is empty";
            return false;
        }
        string actual = npc.CurrentDialogue.Peek().getCurrentDialogue() ?? "";
        if (a.TextContains != null && !actual.Contains(a.TextContains))
        {
            detail = $"expected text containing {Quote(a.TextContains)}, got {Quote(actual)}";
            return false;
        }
        if (a.TextEquals != null && actual.Trim() != a.TextEquals.Trim())
        {
            detail = $"expected text equals {Quote(a.TextEquals)}, got {Quote(actual)}";
            return false;
        }
        return true;
    }

    private static string Quote(string s)
    {
        string trimmed = s.Replace("\n", " ").Replace("\r", "");
        if (trimmed.Length > 80) trimmed = trimmed.Substring(0, 80) + "…";
        return $"\"{trimmed}\"";
    }
}
