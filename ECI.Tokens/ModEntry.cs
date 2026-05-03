using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Locations;

namespace ECI.Tokens;

public class ModEntry : Mod
{
    private DayStartSnapshot? snapshot;
    private readonly HashSet<string> warpFlags = new();

    public override void Entry(IModHelper helper)
    {
        helper.Events.GameLoop.GameLaunched += this.OnGameLaunched;
        helper.Events.GameLoop.SaveLoaded += this.OnSaveLoaded;
        helper.Events.GameLoop.DayStarted += this.OnDayStarted;
        helper.Events.Player.Warped += this.OnWarped;
    }

    // ---------- Token registration ----------

    private void OnGameLaunched(object? sender, GameLaunchedEventArgs e)
    {
        var cp = this.Helper.ModRegistry
            .GetApi<IContentPatcherApi>("Pathoschild.ContentPatcher");

        if (cp is null)
        {
            this.Monitor.Log(
                "Content Patcher not found — ECI tokens will not be registered. " +
                "Install Content Patcher 2.0+ to use the ECI content pack.",
                LogLevel.Error);
            return;
        }

        cp.RegisterToken(this.ModManifest, "PlayerDidToday", this.GetPlayerDidToday);
        cp.RegisterToken(this.ModManifest, "TimeOfDayBucket",
            () => new[] { GetTimeOfDayBucket() });

        this.Monitor.Log("Registered Content Patcher tokens: PlayerDidToday, TimeOfDayBucket.", LogLevel.Trace);
    }

    // ---------- Per-day reset ----------

    private void OnSaveLoaded(object? sender, SaveLoadedEventArgs e)
    {
        // If the player loads a save mid-day, DayStarted won't fire until
        // tomorrow. Capture a baseline now so PlayerDidToday is "ready"
        // immediately instead of returning null.
        this.snapshot = DayStartSnapshot.Capture();
        this.warpFlags.Clear();
    }

    private void OnDayStarted(object? sender, DayStartedEventArgs e)
    {
        this.snapshot = DayStartSnapshot.Capture();
        this.warpFlags.Clear();
    }

    // ---------- Warp-driven flags ----------

    private void OnWarped(object? sender, WarpedEventArgs e)
    {
        if (!e.IsLocalPlayer || e.NewLocation is null)
            return;

        if (e.NewLocation is MineShaft)
            this.warpFlags.Add("enteredMine");
    }

    // ---------- Token providers ----------

    private IEnumerable<string>? GetPlayerDidToday()
    {
        if (!Context.IsWorldReady)
            return null;

        // After SaveLoaded/DayStarted, snapshot is non-null. Defensive check
        // in case of unusual lifecycle paths.
        if (this.snapshot is null)
            return Array.Empty<string>();

        var stats = Game1.player.stats;
        var snap = this.snapshot;
        var flags = new List<string>();

        if (stats.GiftsGiven > snap.GiftsGiven) flags.Add("gaveGift");
        if (stats.FishCaught > snap.FishCaught) flags.Add("caughtFish");
        if (stats.StumpsChopped > snap.StumpsChopped) flags.Add("choppedTree");
        if (Game1.player.passedOut) flags.Add("passedOut");

        flags.AddRange(this.warpFlags);

        return flags;
    }

    private static string GetTimeOfDayBucket()
    {
        // Stardew time is HHMM-ish (600 = 6:00 AM, 1230 = 12:30 PM, 2400 = midnight).
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
