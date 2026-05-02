using StardewModdingAPI;

namespace ECI.Tokens;

/// <summary>Subset of Content Patcher's public API that we consume.</summary>
/// <remarks>
/// Mirrors the shape declared in
/// <c>ContentPatcher.IContentPatcherAPI</c>. We don't reference CP directly —
/// SMAPI hands us a duck-typed proxy when we call
/// <c>Helper.ModRegistry.GetApi&lt;IContentPatcherApi&gt;("Pathoschild.ContentPatcher")</c>.
/// </remarks>
public interface IContentPatcherApi
{
    bool IsConditionsApiReady { get; }

    void RegisterToken(IManifest mod, string name, Func<IEnumerable<string>?> getValue);
}
