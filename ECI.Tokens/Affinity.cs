namespace ECI.Tokens;

/// <summary>Per-NPC, per-axis affinity values, persisted via SMAPI's
/// save data API. Axes are author-defined strings (e.g., "Trust",
/// "Respect", "Romance"); values are signed ints. Missing entries
/// default to 0.
///
/// Values are clamped to [<see cref="MinValue"/>, <see cref="MaxValue"/>]:
/// a $q with the "null" fallback re-asks every day, so response deltas can
/// re-apply indefinitely and would otherwise drift without bound. Authors
/// should treat the range like vanilla friendship points — gates in the
/// YAML should use small thresholds (±5..±20), not the extremes.</summary>
public class Affinity
{
    public const int MinValue = -100;
    public const int MaxValue = 100;

    public Dictionary<string, Dictionary<string, int>> Values { get; set; } = new();

    public int Get(string npc, string axis)
    {
        if (Values.TryGetValue(npc, out var axes) && axes.TryGetValue(axis, out var v))
            return v;
        return 0;
    }

    public void Set(string npc, string axis, int value)
    {
        if (!Values.TryGetValue(npc, out var axes))
            Values[npc] = axes = new Dictionary<string, int>();
        axes[axis] = Math.Clamp(value, MinValue, MaxValue);
    }

    public void Adjust(string npc, string axis, int delta)
    {
        Set(npc, axis, Get(npc, axis) + delta);
    }

    public IEnumerable<(string Npc, string Axis, int Value)> Enumerate()
    {
        foreach (var (npc, axes) in Values)
            foreach (var (axis, value) in axes)
                yield return (npc, axis, value);
    }
}

/// <summary>The shape of responses.json (loaded from the mod folder).
/// Maps a Stardew dialogue-answer ID (the value Stardew adds to
/// <c>Game1.player.dialogueQuestionsAnswered</c> when the player picks
/// that response) to the per-NPC, per-axis deltas it should apply.
///
/// Example:
/// <code>
/// {
///   "leah_q_art_yes":   { "Leah": { "Trust": 5, "Romance": 2 } },
///   "leah_q_art_no":    { "Leah": { "Trust": -10, "Respect": -5 } }
/// }
/// </code>
/// </summary>
public class ResponsesConfig
{
    public Dictionary<string, Dictionary<string, Dictionary<string, int>>> Responses { get; set; } = new();
}
