namespace ECI.Tokens;

/// <summary>Mod-provided API, returned from <see cref="ModEntry.GetApi"/>.
/// Other mods (e.g. ECI.TestHarness) consume it by declaring a matching
/// interface and calling
/// <c>Helper.ModRegistry.GetApi&lt;IEciTokensApi&gt;("eavalenzuela.ECI.Tokens")</c>;
/// SMAPI (Pintail) proxies the calls by signature.
///
/// Only simple parameter/return types (int, string, string[]) are used so
/// the proxy mapping stays trivial. NPC and axis names are canonicalized
/// case-insensitively against the focal NPC / axis lists, matching what
/// the Affinity&lt;NPC&gt;&lt;Axis&gt; CP tokens read.</summary>
public class EciApi
{
    private readonly ModEntry mod;

    internal EciApi(ModEntry mod)
    {
        this.mod = mod;
    }

    /// <summary>Current affinity value for an NPC axis (0 if unset).</summary>
    public int GetAffinity(string npc, string axis)
        => this.mod.AffinityStore.Get(ModEntry.CanonicalNpc(npc), ModEntry.CanonicalAxis(axis));

    /// <summary>Set an NPC axis to an absolute value (clamped to the
    /// Affinity range).</summary>
    public void SetAffinity(string npc, string axis, int value)
        => this.mod.AffinityStore.Set(ModEntry.CanonicalNpc(npc), ModEntry.CanonicalAxis(axis), value);

    /// <summary>Shift an NPC axis by a delta (clamped to the Affinity
    /// range).</summary>
    public void AdjustAffinity(string npc, string axis, int delta)
        => this.mod.AffinityStore.Adjust(ModEntry.CanonicalNpc(npc), ModEntry.CanonicalAxis(axis), delta);

    /// <summary>The NPCs that have registered Affinity CP tokens.</summary>
    public string[] GetTrackedNpcs()
        => ModEntry.GetFocalNpcs();

    /// <summary>The affinity axes registered per NPC (Trust/Respect/Romance).</summary>
    public string[] GetTrackedAxes()
        => ModEntry.GetAffinityAxes();

    /// <summary>Today's PlayerDidToday flags (without the internal
    /// readiness sentinel). Empty before a save is loaded.</summary>
    public string[] GetPlayerDidTodayFlags()
        => this.mod.CurrentPlayerDidTodayFlags();
}
