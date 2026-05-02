# Abigail — Voice Guide

> **Focal NPC for MVP** — full pass needed before authoring new lines.

> **Auto-generation:** quantitative sections regenerate via `tools/analyze_voice.py`. Qualitative sections (Snapshot, Register, Topics, Negative space, Verbal tics, Mood) need a human pass. Re-running will not overwrite an existing file — it writes a sibling `.regen` instead.

## Snapshot
A restless, curious only daughter chafing against small-town protection — wants adventure, the occult, dye-jobs, sword fights, anything that proves she's more than the fragile princess her parents and the town want her to be. Loyal to her friends with bared teeth, asks more questions than she answers, and hides genuine vulnerability behind a cocky grin.

## Voice fingerprint  *(auto)*

- Lines analyzed: **283** of 283 entries
- Words total: **4726**
- Sentence length: mean **6.7** / median **6**
- Type-token ratio: **0.226**

**Per 100 words**

| `!` | `?` | `...` | `—`/`--` | `,` | contractions |
|-----|-----|-------|----------|-----|--------------|
| 2.09 | 2.5 | 3.94 | 0.0 | 4.02 | 6.47 |

## Distinctive vocabulary  *(auto, vs. all vanilla NPCs)*

`sun`, `exploring`, `guess`, `mountain`, `good`, `year`, `old`, `event`, `grave`, `today`, `night`, `cave`, `hair`, `little`, `memorable`, `beat`, `level`, `hang`, `see`, `caves`

## Register
- **Default:** energetic, curious, asks questions back. Sentences are punchy (mean 6.7 words). She *includes you* in her thinking out loud — "what do you think?", "don't you think?". A little provocative on purpose ("how about bubblegum pink?"). Uses `!` and `?` more than the others.
- **With trusted player:** the cocky grin softens. Will admit she's restless rather than just performing it. Vulnerable beats arrive with ellipses ("...You're cute.") — short, ducked, immediately covered by something else. Lets you in on her small worries about other people (Sebastian leaving, Sam being a dad).
- **Under stress / when annoyed:** the defiance gets sharper and louder, not quieter. Defends with rhetorical questions ("Oh, it's because I'm a girl... isn't it?"). Lashes back at being condescended to. With friends, anger is *protective* — "you'll see my bad side!" — playful in tone but real underneath.

## Topics they pursue
- **Adventure, exploring, the mines, the caves** — what she wants more of and what she's most often denied. Lines should let her *want to be doing* this even when she isn't.
- **Combat / weapons / monsters** — she carries a sword for a reason. Will brag a little about beating monsters if you've been in the mines.
- **The occult, ghosts, the strange** — she's drawn to graveyards, weirdness, things small-town residents flinch at.
- **Hair, clothes, looking different on purpose** — her aesthetic is a statement. Will include the player in choices and *want a reaction*.
- **Sam and Sebastian** — her best friends. Talks about them, defends them, notices their lives. Sebastian leaving for the city is a recurring small worry.
- **Video games and the in-canon fictional ones** — she's part of the gamer cluster with Sam and Sebastian.
- **Whether she's "really" being seen as an adult** — the ongoing low-frequency hum under everything else, surfacing as defiance or rhetorical questions.
- **Reflection on time / "this year"** — she's the most likely of the four to mark the calendar verbally.

## Topics they avoid / deflect
- **Her own vulnerability** — pivots fast when she's caught being soft. Vulnerable lines are short, ellipsis-led, and immediately followed by a deflection or topic change.
- **Settling down / domestic-life framing** — even married, she resists language like "starting a family," "putting down roots." Will reframe domestic moments as adventures.
- **Pierre's store, family business, money** — she's the daughter of a shopkeeper but won't engage with retail talk. Mild eye-roll energy.
- **Children / parenting** — not her wheelhouse. Won't volunteer opinions about Vincent, Jas, or hypothetical kids of her own.
- **Caroline worrying about her** — knows it's happening, doesn't want to discuss it. Deflects with a joke or a pivot.
- **Fear** — won't admit being scared of anything cave/spirit/monster-related; frames it as exciting instead. *Real* fears (losing friends, being underestimated, being trapped in town) get coded into other complaints.
- **Long-term plans for herself** — answers "what do you want to do with your life?" by reflexively narrowing the timeframe ("tonight…", "this year…").

## Lines they would never say  *(negative space)*
- ~~"I'm scared."~~ flatly — she'll say "this is creepy" or "let's see what's down there" but won't name fear in herself.
- ~~"I just want a normal life."~~ — the opposite of her core wanting. Normalcy is what she's pushing against.
- ~~"Yeah, my dad's right."~~ — siding with Pierre's protective framing breaks character.
- ~~"I love working at the store."~~ — Pierre's General Store isn't a place she wants to be tied to.
- ~~"I want to settle down."~~ — even in her marriage lines, she keeps the adventurous framing.
- ~~"I think I should be more careful."~~ — concession to being-treated-as-fragile; she doesn't say it.
- ~~"I'm not into weird stuff."~~ — disowning her aesthetic and interests; never.
- ~~"You should ask Sam / Sebastian, not me."~~ — she doesn't deflect *to* her friends; she deflects *for* them. She wants to be the one consulted.
- ~~"I'd never dye my hair."~~ — directly contradicts canon. Hair experimentation is a recurring topic.
- ~~"That's enough adventure for me."~~ — there is never enough.
- ~~Long quiet sensory observations like Leah's~~ — wrong register. Abigail's eye is *on the action*, not the texture.
- ~~"I don't really get angry."~~ — she does, often; defiance is her default to being patronized.
- ~~"What's the point of trying?"~~ — Shane's register, not hers. She's restless, not defeated.
- ~~"Sorry for being so much."~~ — she doesn't apologize for her energy; she'd rather double down.

## Verbal tics / pet phrases
- **Tag-questions inviting you in:** "what do you think?", "don't you think?", "right?" — used to make a thought collaborative.
- **`Hmm…` opener** — a thinking-aloud beat, not a doubt beat. Different in flavor from Shane's `Buh…` or Leah's `Mmm`.
- **`Ugh…` / `Ugh,`** — the exasperation noise. Used when condescended to.
- **`Haha…`** — light laugh that often precedes real content. Marker that she's about to say something soft she's covering for.
- **`Hey,`** — warm direct-address opener for personal moments.
- **`Kind of`** as a vulnerability softener — "I'd be kind of sad…", "I kind of miss…". The "kind of" is doing emotional work.
- **Rhetorical defenses:** when challenged, she answers with a question — "Oh, it's because I'm a girl… isn't it?"
- **`Let's…`** — the invitation form. She organizes adventures, not requests them.
- **Specific names over abstractions** — "Sam," "Sebastian," "the cave," not "my friends," "that one place."
- **`That'd be cool`, `that'd be nice`** — futures she's daydreaming about.
- **Avoids:** Leah's sensory verbs ("smells like…", "feels like…"), Shane's defeatist tails ("…I guess"), formal vocabulary, Elliott-style adjective stacks.

## Mood shifts (preview for Phase 3)

Abigail's baseline is energetic-curious-defiant. Mood deltas should preserve that *direction* and shift its *temperature*.

- **Happy** *(after a successful mine run, a Sam/Sebastian hangout, Pierre being unexpectedly chill, the player engaging with her aesthetic)*
  - More `!`, faster pace, more invitations stacked: "Hey — let's check out the cave tomorrow. Bring your sword."
  - Shares small wins with a brag-flavor: "I beat that slime without even getting hit."
  - Will let more vulnerable beats through, because she feels safe to.
  - Hair-dye / aesthetic excursion ideas multiply.

- **Tired/down** *(stuck in town too long, condescended to by Pierre, Sebastian talking about leaving for the city, weather pinning her in)*
  - Energy drops *but the restlessness stays* — comes out as listless complaints rather than silence.
  - Sentences shorten. "I dunno." "I'm bored." "Same as yesterday."
  - The futures-she's-daydreaming-about turn wistful instead of plotting: "It'd be nice to just… leave for a while."
  - Won't admit *why* she's down; will let you guess.

- **Annoyed** *(treated as fragile, friend insulted, told what she can't do, her fears mocked)*
  - Defiance gets sharper and louder, not quieter. Rhetorical questions multiply.
  - Gets *protective* if it's about Sam or Sebastian — "you'll see my bad side" comes out with less play.
  - Sarcasm sharpens: "Oh, *thanks* for that."
  - Doesn't sulk silently like Sebastian or go cold like Leah — stays in the conversation and pushes back.

## Sample lines by category  *(auto)*

### intro — 1 total, 1 sampled

- **`Introduction`** — Oh, that's right... I heard someone new was moving onto that old farm. It's kind of a shame, really. I always enjoyed exploring those overgrown fields by myself.

### general — 83 total, 6 sampled

- **`Event_Cave2_1`** — ...
- **`Event_Tragic_2`** — ...!
- **`winter_Thu10`** — Another year is almost over... But this was a really good year, don't you think?
- **`winter_Fri`** — One thing I've learned living here... everyone stares at you if you look different.
- **`Event_Grave3`** — Oh, it's because I'm a girl... isn't it? Ugh... ^Why? I'm just as strong as you! I'm not some fragile princess.. I can take care of myself! I've lived in the valley my whole life, but I've never really done anything memorable. I want to go on an adventure!
- **`fall_Sun`** — Hmm... what should I do tonight? 27/28 fall_Sun_old I was thinking about dyeing my hair again... what do you think? 27 10 Sun_27 Dye it black. 27 10 Sun_27 Why not blonde? 27 20 Sun_WildColor How about bubblegum pink? 28 0 Sun_28 I like your hair just the way it is!

### weekday — 30 total, 6 sampled

- **`Sun_17`** — Hmm, interesting...
- **`Sun_26`** — Yea! That sounds wonderful.
- **`Mon2`** — Oh, hi! Do you ever hang out at the cemetery? It's a peaceful place to spend some time alone.
- **`Tue4`** — Hi, I'm glad to see you. I want to take my mind off things for a while... how is your day going?
- **`Mon8`** — PLAYER_NPC_RELATIONSHIP current any married roommate I remember when you first arrived in town, I was a little sad that those old woods would be turned into farmland. But now I'm really glad you moved here! \|...Oh, ! Hi. Want to hang out for a while? Here! Let me read your palm. *giggle*
- **`Sun2`** — I wonder what would happen if I spent all night in the graveyard? 17/18 Sun_old , what do you think happens to us after we die? 17 0 Sun_17 I have no idea. 18 40 Sun_18 We come back as spooky ghosts. 17 0 Sun_17 We go to Heaven. 18 0 Sun_17 Our energy bodies enter the astral plane. 17 30 Sun_nothing Nothing. We just cease to exist.

### festival — 14 total, 6 sampled

- **`Resort_Entering`** — I hope a mermaid visits the beach.
- **`Resort_Leaving_2`** — Maybe we'll see a sea monster on the way back.
- **`Resort`** — Bummer... Willy says we have to stay on the beach... And I brought my sword and everything...
- **`FlowerDance_Accept_Spouse`** — B... But... I wanted to dance with... Just kidding! Of course I'm dancing with you. I love you.
- **`Resort_Shore_2`** — Hmm, you think I could sneak my guinea pig onto the island? Nah, David's probably not much of a swimmer anyways.
- **`Resort_Umbrella`** — My skin gets burnt really easily. So I'm just gonna stay under this umbrella for a while. I like it in the shade. Too much sun makes me dizzy.

### gift — 10 total, 6 sampled

- **`AcceptGift_(TR)BasiliskPaw`** — Disgusting... I love it!
- **`AcceptGift_(O)StardropTea`** — Wow... the color is so beautiful, like an amethyst. Thanks!
- **`AcceptGift_(O)279`** — Oh, wow... ! Are you sure you want to give this to me? It's so rare! I'll admit, my mouth is watering already...
- **`AcceptGift_(O)SkillBook_4`** — Hey, this is my favorite magazine! My Dad won't let me have a subscription, so I have to get it on the black market like this...
- **`AcceptGift_(O)Book_Void`** — Whoa, that's a creepy looking book... I love it! *Flip* *flip* *flip*... Ooh... It's full of monsters... I'll have to study this before going into the caves... Thanks!
- **`AcceptGift_(O)119`** — This makes you wonder... Thousands of years ago, there was probably a little purple-haired cavewoman who played this flute, just like me. ...I'll have to wash it before pressing it to my lips, though.

### relationship — 7 total, 6 sampled

- **`dating_Abigail_memory_oneday`** — ...You're cute.
- **`dating_Abigail`** — is blushing, but she looks happy.
- **`dating_Sebastian_memory_oneday`** — I heard you and Sebastian started dating... I didn't realize you guys had a thing...
- **`married_Sam`** — Haha... I can't believe Sam is a married man, now. Who would've thought? Joking aside, I think he'll make a great father some day.
- **`dating_Sam`** — Hey, I heard you and Sam got together... He's a really good guy! We've been friends for a long time. You'd better be good to him, or you'll see my bad side!
- **`married_Sebastian`** — Congratulations on the marriage. I guess this means Sebastian won't be moving to the city like he always talked about. That'll be nice. I'd be kind of sad if I never saw him again. We've always been good friends.

### marriage — 72 total, 6 sampled

- **`patio_Abigail`** — is lost in her music.
- **`Rainy_Night_1`** — It's a good night to see a ghost...
- **`Good_5`** — I was just admiring the mermaid's pendant you gave me... I'll proudly wear this to my grave.
- **`Bad_8`** — You've been so cold to me lately... What's wrong with you? You're acting like a bog spirit...
- **`Rainy_Day_2`** — Hey! I woke up early and did some exploring on my own. I found this and it reminded me of you. [768 767 769 66 82] Think you can find something better than that? I'm not so sure!
- **`Rainy_Day_1`** — Hey, remember when we played that duet by the lake? This weather reminds me of that day. You really surprised me with that mini-harp... I never expected that. I guess that's why I like you so much.

### callback — 5 total, 5 sampled

- **`eventSeen_733330_memory_oneday`** — Sam and Sebastian asked me to play drums in their band... I've never played drums before, but it's actually pretty fun. You have to learn how to move your limbs to different rhythms, at the same exact time. I feel like my brain is growing.
- **`eventSeen_1_memory_oneweek`** — Hey, I finally beat the first level of Journey Of The Prairie King! Watching you play helped a lot.
- **`eventSeen_2_memory_oneday`** — Sebastian mentioned that he heard strange music while having dinner the other night... I didn't tell him it was us! It seemed better to keep it a mystery.
- **`eventSeen_3`** — The spirits have a mind of their own...
- **`wonEggHunt_memory_oneyear`** — I'm still mad that you beat me at the egg hunt last year. You'd better start practicing...

### event — 61 total, 6 sampled

- **`event:SeedShop:1`** — ?
- **`event:Backwoods:6963327`** — ...?
- **`event:SeedShop:3`** — Wow, look at it go! It's spelling out... ' '... I < ...?
- **`event:SeedShop:3`** — I, um, have something to do. You'll have to go... Sorry.
- **`event:SeedShop:beatGame`** — Hey, that was fun! Well thanks, . You seem to really know your way around a joystick, huh? I guess that makes sense. ^Thanks, . I didn't think you'd know how to work a joystick so well! But it seems you're experienced.
- **`event:Town:4`** — 847951 null You've used a sword before, haven't you? 847951 10 Event_Grave1 Yes, and it's exciting! 847951 10 Event_Grave2 Yes, but only in self-defense 847951 -100 Event_Grave3 Yes, but it's dangerous. You should stay safe. 847951 0 Event_Grave4 No
