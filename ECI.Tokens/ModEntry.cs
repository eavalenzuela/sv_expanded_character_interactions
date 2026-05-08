using HarmonyLib;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Locations;

namespace ECI.Tokens;

public class ModEntry : Mod
{
    // Stardew's Dialogue.chooseResponse adds playerResponse.id (which is
    // the *question* id, not the response id) to dialogueQuestionsAnswered.
    // The response identity (e.g. "leah_q_art_yes") only lives on the
    // Response argument as `responseKey`. So polling dialogueQuestionsAnswered
    // can't tell which option was picked. The Harmony postfix below is the
    // only reliable hook into the per-response selection event.
    internal static ModEntry? Instance;

    private DayStartSnapshot? snapshot;
    private readonly HashSet<string> warpFlags = new();

    private Affinity affinity = new();
    private ResponsesConfig responses = new();

    private static readonly string[] FocalNpcs = { "Leah", "Shane", "Abigail", "Sebastian" };
    private static readonly string[] AffinityAxes = { "Trust", "Respect", "Romance" };

    public override void Entry(IModHelper helper)
    {
        Instance = this;

        helper.Events.GameLoop.GameLaunched += this.OnGameLaunched;
        helper.Events.GameLoop.SaveLoaded += this.OnSaveLoaded;
        helper.Events.GameLoop.Saving += this.OnSaving;
        helper.Events.GameLoop.DayStarted += this.OnDayStarted;
        helper.Events.Player.Warped += this.OnWarped;

        helper.ConsoleCommands.Add(
            "eci_affinity",
            "Inspect or set affinity. Usage: eci_affinity show [<NPC>] | eci_affinity set <NPC> <axis> <value>",
            this.OnAffinityCommand);

        var harmony = new Harmony(this.ModManifest.UniqueID);
        harmony.Patch(
            original: AccessTools.Method(typeof(Dialogue), nameof(Dialogue.chooseResponse)),
            postfix: new HarmonyMethod(typeof(ModEntry), nameof(ChooseResponsePostfix)));
    }

    /// <summary>Harmony postfix on Dialogue.chooseResponse. Fires after
    /// vanilla has applied friendship and added the question id to
    /// dialogueQuestionsAnswered. We read the response's responseKey
    /// (the unique id like "leah_q_art_yes") and apply our affinity
    /// deltas. No-op if the key isn't in responses.json.</summary>
    public static void ChooseResponsePostfix(Response response)
    {
        if (response?.responseKey == null) return;
        Instance?.ApplyResponseDeltas(response.responseKey);
    }

    // ---------- Token registration ----------

    private void OnGameLaunched(object? sender, GameLaunchedEventArgs e)
    {
        // Load the responses config from the mod folder. Missing or empty
        // file is fine — branching dialogue authoring just hasn't started.
        try
        {
            this.responses = this.Helper.Data.ReadJsonFile<ResponsesConfig>("responses.json")
                            ?? new ResponsesConfig();
            this.Monitor.Log(
                $"Loaded responses.json with {this.responses.Responses.Count} response mappings.",
                LogLevel.Info);
        }
        catch (Exception ex)
        {
            this.Monitor.Log($"Failed to read responses.json: {ex.Message}", LogLevel.Warn);
            this.responses = new ResponsesConfig();
        }

        var cp = this.Helper.ModRegistry
            .GetApi<IContentPatcherApi>("Pathoschild.ContentPatcher");
        if (cp is null)
        {
            this.Monitor.Log(
                "Content Patcher not found — ECI tokens will not be registered.",
                LogLevel.Error);
            return;
        }

        cp.RegisterToken(this.ModManifest, "PlayerDidToday", this.GetPlayerDidToday);
        cp.RegisterToken(this.ModManifest, "TimeOfDayBucket",
            () => new[] { GetTimeOfDayBucket() });

        // Register affinity tokens — one per (NPC, axis) since the simple
        // Func RegisterToken form doesn't support input arguments. CP only
        // accepts alphabetical token names (no underscores/digits), so the
        // shape is Affinity<NPC><Axis> e.g. AffinityLeahTrust.
        foreach (string npc in FocalNpcs)
        {
            foreach (string axis in AffinityAxes)
            {
                string n = npc, a = axis; // capture
                cp.RegisterToken(
                    this.ModManifest,
                    $"Affinity{n}{a}",
                    () => new[] { this.affinity.Get(n, a).ToString() });
            }
        }

        this.Monitor.Log(
            $"Registered CP tokens: PlayerDidToday, TimeOfDayBucket, " +
            $"and {FocalNpcs.Length * AffinityAxes.Length} Affinity<NPC><Axis> tokens.",
            LogLevel.Info);
    }

    // ---------- Save data lifecycle ----------

    private void OnSaveLoaded(object? sender, SaveLoadedEventArgs e)
    {
        this.snapshot = DayStartSnapshot.Capture();
        this.warpFlags.Clear();

        this.affinity = this.Helper.Data.ReadSaveData<Affinity>("eci_affinity") ?? new Affinity();

        int totalEntries = this.affinity.Values.Sum(npc => npc.Value.Count);
        this.Monitor.Log(
            $"OnSaveLoaded: loaded affinity for {this.affinity.Values.Count} NPCs " +
            $"({totalEntries} axis entries).",
            LogLevel.Info);
    }

    private void OnSaving(object? sender, SavingEventArgs e)
    {
        this.Helper.Data.WriteSaveData("eci_affinity", this.affinity);
    }

    private void OnDayStarted(object? sender, DayStartedEventArgs e)
    {
        this.snapshot = DayStartSnapshot.Capture();
        this.warpFlags.Clear();
    }

    // ---------- Warp + dialogue-answer hooks ----------

    private void OnWarped(object? sender, WarpedEventArgs e)
    {
        if (!e.IsLocalPlayer || e.NewLocation is null) return;
        if (e.NewLocation is MineShaft)
            this.warpFlags.Add("enteredMine");
    }

    private void ApplyResponseDeltas(string responseId)
    {
        if (!this.responses.Responses.TryGetValue(responseId, out var npcDeltas))
            return;

        foreach (var (npc, axisDeltas) in npcDeltas)
        {
            foreach (var (axis, delta) in axisDeltas)
            {
                this.affinity.Adjust(npc, axis, delta);
                this.Monitor.Log(
                    $"Affinity Δ from response '{responseId}': {npc}.{axis} {(delta >= 0 ? "+" : "")}{delta} → {this.affinity.Get(npc, axis)}",
                    LogLevel.Info);
            }
        }
    }

    // ---------- Console command ----------

    private void OnAffinityCommand(string command, string[] args)
    {
        if (args.Length == 0)
        {
            this.Monitor.Log(
                "Usage:\n  eci_affinity show [<NPC>]\n  eci_affinity set <NPC> <axis> <value>",
                LogLevel.Info);
            return;
        }
        switch (args[0].ToLowerInvariant())
        {
            case "show":
                this.ShowAffinity(args.Length > 1 ? args[1] : null);
                break;
            case "set" when args.Length >= 4 && int.TryParse(args[3], out int v):
                this.affinity.Set(args[1], args[2], v);
                this.Monitor.Log($"Set {args[1]}.{args[2]} = {v}.", LogLevel.Info);
                break;
            default:
                this.Monitor.Log(
                    "Bad arguments. Usage: eci_affinity show [<NPC>] | eci_affinity set <NPC> <axis> <value>",
                    LogLevel.Error);
                break;
        }
    }

    private void ShowAffinity(string? filterNpc)
    {
        var entries = this.affinity.Enumerate()
            .Where(t => filterNpc is null || t.Npc.Equals(filterNpc, StringComparison.OrdinalIgnoreCase))
            .OrderBy(t => t.Npc).ThenBy(t => t.Axis)
            .ToList();
        if (entries.Count == 0)
        {
            this.Monitor.Log(
                filterNpc is null ? "(no affinity entries yet)"
                                  : $"(no affinity entries for {filterNpc})",
                LogLevel.Info);
            return;
        }
        var lines = new List<string> { "=== ECI Affinity ===" };
        foreach (var (npc, axis, value) in entries)
            lines.Add($"  {npc,-12} {axis,-10} {value}");
        this.Monitor.Log(string.Join("\n", lines), LogLevel.Info);
    }

    // ---------- Existing PlayerDidToday + TimeOfDayBucket ----------

    /// <summary>Sentinel value always present in PlayerDidToday's value set.
    /// CP's ModSimpleValueProvider marks a lambda-form token as "not ready"
    /// when its values are empty (see CP source). Authors never reference
    /// this sentinel.</summary>
    private const string ReadinessSentinel = "_active";

    private IEnumerable<string> GetPlayerDidToday()
    {
        var flags = new List<string> { ReadinessSentinel };
        if (!Context.IsWorldReady || this.snapshot is null) return flags;

        var stats = Game1.player.stats;
        var snap = this.snapshot;

        if (stats.GiftsGiven > snap.GiftsGiven) flags.Add("gaveGift");
        if (stats.FishCaught > snap.FishCaught) flags.Add("caughtFish");
        if (stats.StumpsChopped > snap.StumpsChopped) flags.Add("choppedTree");
        if (Game1.player.passedOut) flags.Add("passedOut");
        flags.AddRange(this.warpFlags);
        return flags;
    }

    private static string GetTimeOfDayBucket()
    {
        int t = Game1.timeOfDay;
        if (t < 1100) return "morning";
        if (t < 1500) return "midday";
        if (t < 1900) return "evening";
        return "late";
    }
}

internal sealed record DayStartSnapshot(uint GiftsGiven, uint FishCaught, uint StumpsChopped)
{
    public static DayStartSnapshot Capture()
    {
        var s = Game1.player.stats;
        return new DayStartSnapshot(s.GiftsGiven, s.FishCaught, s.StumpsChopped);
    }
}
