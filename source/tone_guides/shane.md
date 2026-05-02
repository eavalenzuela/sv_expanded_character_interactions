# Shane — Voice Guide

> **Focal NPC for MVP** — full pass needed before authoring new lines.

> **Auto-generation:** quantitative sections regenerate via `tools/analyze_voice.py`. Qualitative sections (Snapshot, Register, Topics, Negative space, Verbal tics, Mood) need a human pass. Re-running will not overwrite an existing file — it writes a sibling `.regen` instead.

## Snapshot
A cynical, depression-flattened ex-Joja employee who lives with his aunt and Jas; uses sarcasm and self-deprecation to deflect, drinks to cope, and softens slowly when someone earns his trust — at which point his guarded humor turns into something closer to gratitude.

## Voice fingerprint  *(auto)*

- Lines analyzed: **225** of 225 entries
- Words total: **3511**
- Sentence length: mean **6.0** / median **5**
- Type-token ratio: **0.256**

**Per 100 words**

| `!` | `?` | `...` | `—`/`--` | `,` | contractions |
|-----|-----|-------|----------|-----|--------------|
| 0.68 | 2.53 | 7.52 | 0.0 | 3.79 | 6.35 |

## Distinctive vocabulary  *(auto, vs. all vanilla NPCs)*

`buh`, `joja`, `game`, `life`, `tunnelers`, `hens`, `pizza`, `tip`, `jas`, `breakdown`, `talking`, `round`, `bass`, `alone`, `drinking`, `enjoyed`, `eggs`, `marnie`, `work`, `today`

## Register
- **Default:** terse, dismissive, often hostile — wants you to leave him alone. Short sentences ending in `...` or a flat period. Sarcasm is the first reflex. Question-asks come out as accusations ("What? What do you want?").
- **With trusted player:** still hesitant and ellipsis-heavy, but the sarcasm softens into self-deprecating humor. Will admit things he wouldn't say to anyone else — about Joja, about drinking, about feeling stuck. Compliments are awkward and qualified ("This is actually really nice, though."). Reveals affection through plans for *future* shared things, not direct statements.
- **Under stress / when annoyed:** retreats to monosyllables and hostility. Drinks more, mentions it more. Will lash out — "Go away," "Don't you have work to do?" — then sometimes spiral into a self-loathing monologue if pushed (the "I hated my job at JojaMart, but now that I'm unemployed I feel even worse" register).

## Topics they pursue
- **Chickens, especially Charlie** — the one place his voice goes warm without irony. Will volunteer chicken trivia, chicken health, chicken personalities.
- **Tunnelers (gridball)** — game scores, betting on outcomes, players. Often paired with drinking.
- **Joja, work, money** — almost always negative. Rants about shelf-stocking, about being underpaid, about being unemployed after.
- **Beer, the saloon, frozen pizza, video games** — his comfort menu; mentions casually as habit, not as something to share.
- **Jas and Marnie** — protective, responsibility-tinged. He's not effusive but they're load-bearing for him.
- **(Post-arc) recovery, sobriety, "getting his life together"** — careful, fragile register; never declarative ("I'm fixed"), always provisional ("I'm trying").

## Topics they avoid / deflect
- **His own depression / mental health** — outside the canonical 6-heart breakdown, he never names it. Will gesture (`*sigh*`, ellipses, "every day is the same") but never says the word.
- **Jas's parents / how Jas came to live with Marnie** — load-bearing trauma, off-limits in casual talk.
- **His own past** — pre-Joja, family of origin, why he ended up in Pelican Town. He'll mention "the city" abstractly but not specifics.
- **Compliments to himself or about himself** — deflects with sarcasm or self-deprecation. If you praise him, expect "Heh," or "...thanks, I guess."
- **Hopes for the future** — pre-arc, anything aspirational gets a defeated joke. Post-arc, he'll allow small specifics (a Tunnelers game, a chicken plan) but not big ones.
- **Romantic feeling, said directly** — even married, he leans on understated affection (Charlie updates, light teasing) rather than declarations.

## Lines they would never say  *(negative space)*
- ~~"What a beautiful day!"~~ — Shane never voluntarily celebrates weather. Sun is "Vitamin D" he begrudgingly tolerates; rain is mild relief from being seen.
- ~~"I'm so excited!"~~ — `!` rate is 0.68/100w; raw enthusiasm reads false on him. Even at his happiest, he understates ("This is actually really nice, though.").
- ~~"I love you."~~ said unprompted — too direct. Even married, his affection comes through Charlie updates and dry humor.
- ~~"Let me tell you about myself."~~ — Shane never volunteers his own backstory or feelings unsolicited; you have to corner him.
- ~~"You should try [self-help / new hobby / fresh start]!"~~ — he doesn't proselytize positivity; that's Penny's lane, or Caroline's, not his.
- ~~"Things are going to be okay."~~ — too declarative, too clean. He hedges: "...I'm trying," "...we'll see."
- ~~"I had a great day at work."~~ — work is never positively framed in canon. Even post-Joja, work is something to survive.
- ~~"That's a great idea!"~~ as agreement — he agrees with skepticism: "...Heh, sure," "Yeah, I guess that could work."
- ~~Long flowing sentences with lush adjectives~~ — that's Elliott's register. Shane's median sentence is 5 words and he avoids descriptors.
- ~~Apologies that aren't qualified~~ — even his canonical apology comes out as "...Yeah, me too" rather than "I'm sorry."
- ~~Naming emotions cleanly~~ — never "I'm sad," "I'm angry," "I'm scared." He'll talk *around* them or describe symptoms (insomnia, drinking, "I feel even worse").

## Verbal tics / pet phrases
- **`Buh...`** — exhaled, deflated opener. Use sparingly; one of his strongest fingerprints.
- **`Heh.`** — single-syllable laugh, often after a self-deprecating beat. Replaces "haha" or "lol"; never "lol".
- **`Welp...`** — resignation opener for transitions ("welp, that's that").
- **`Hoo-boy.`** — only when socially cornered into something light he didn't ask for.
- **Bracketed stage directions:** `*sigh*`, `*ahem*`, `*squish*` — used to gesture at reactions he won't name.
- **Sentence-tail disclaimers:** `...I guess`, `...you know`, `...Anyway.`, `...whatever.` — soft denials of the thing he just said.
- **Trailing ellipses on emotional admissions** — when something matters, the sentence loses energy: "I... wasn't really expecting this..."
- **Frozen pizza & cold ones** as a recurring shorthand for "my life is fine, leave me alone."
- **Hedge words:** "kind of," "sort of," "maybe," "I guess" — he commits to almost nothing without one.
- **Avoids:** "totally," "absolutely," "definitely," "amazing," "fantastic," exclamation chains.

## Mood shifts (preview for Phase 3)

Shane's *baseline* register is already "tired-down" relative to other NPCs — these deltas are calibrated against his own midline, not the cast average.

- **Happy** *(rare; usually post-arc, after a good Tunnelers result, or a Charlie/Jas moment)*
  - Sentences run a beat longer; ellipses fewer.
  - One quiet declarative slips through without a hedge: "Charlie laid an egg today. A real one."
  - Will offer instead of refuse: "Hey... if you're not busy, the Tunnelers are on tonight."
  - Still no exclamation marks. Still no "I love…". The sign of happy-Shane is presence, not enthusiasm.

- **Tired/down** *(default-default; deeper variant on Mondays / mornings / post-event-1 / Joja-shift mention)*
  - Reverts hard to monosyllables: "Yeah." "Whatever." "...Mh."
  - Ellipses spike. Stage directions appear: `*sigh*`, `*long pause*`.
  - Self-loathing surfaces: "Wasted another day." "Should've stayed in bed."
  - Mentions of beer, bed, blinds, frozen pizza increase. Vocabulary shrinks to comfort objects.

- **Annoyed** *(low hearts default, after being pestered, or when Joja/Morris mentioned)*
  - Hostile imperatives: "Go away." "Don't you have something to do?"
  - Sarcasm sharpens to acid: "Oh, *great*. Just what I needed."
  - Will refuse to engage at all: "...No." (one-word lines, a Shane signature).
  - Harsher percussives: `Tch.`, `Ugh.` instead of his softer `Heh.`

## Sample lines by category  *(auto)*

### general — 19 total, 6 sampled

- **`event_noLoan3`** — Oh, wow...
- **`event_apologize1`** — ...Yeah, me too.
- **`event_apologize2`** — I know... that's why I stopped by, to tell you about it.
- **`GreenRain`** — I don't have to go into work today, so I'm not complaining...
- **`pamHouseUpgrade`** — I heard you built Pam a house... That's really generous... You know, I could use a hundred thousand gold myself... *ahem* ...ah ...Just kidding. ...Heh.
- **`event_stadium2`** — Oh really? I'm surprised... Didn't you move to Stardew Valley to escape the noise of the city? I mean... Don't get me wrong, I totally understand. My life in Pelican Town is pretty bland, you know.

### weekday — 34 total, 6 sampled

- **`Fri`** — Don't you have work to do?
- **`Tue`** — What? What do you want? Go away.
- **`Tue4`** — Every time I try something new it goes horribly wrong. You learn to just stay in a shell.
- **`Tue8`** — We should go to a Tunnelers game some time. When I go by myself, I usually drink way too much beer.
- **`Wed4`** — Joja *sigh* ...Every day is the same. Stocking those horrible shelves, going to the saloon, tossing and turning all night. \|I hated my job at JojaMart, but now that I'm unemployed I feel even worse.
- **`Sun4`** — Hmm... it's . Should I throw a frozen pizza in the microwave, or should I wait? \|\|If the Tunnelers win, I'll knock back a cold one to celebrate. If they lose? I'll have a cold one to drown my sorrows.

### festival — 9 total, 6 sampled

- **`FlowerDance_Decline`** — ...No.
- **`Resort_Entering`** — Buh... hope the bar's open.
- **`Resort_Bar`** — Phew... feels good to have a cold drink... Or maybe a few...
- **`FlowerDance_Accept_Spouse`** — Dance? Hoo-boy. Okay... let me chug a few more of these first...
- **`Resort_Leaving`** — Welp... got my year's supply of Vitamin D. Now I can play video games with the blinds shut the rest of the year.
- **`Resort_Shore`** — That's right... I'm not wearing any shoes or socks. Some call it a public health risk. The crabs seem to enjoy it, though.

### gift — 4 total, 4 sampled

- **`AcceptBirthdayGift_Loved`** — Oh, is it my birthday? I was hoping I'd forget. This is actually really nice, though. Thank you.
- **`AcceptBirthdayGift_Liked`** — Oh, is it my birthday? That's right... I almost forgot. Thanks.
- **`AcceptGift_(O)StardropTea`** — Heh... thanks. Tastes just like beer.
- **`AcceptGift_(O)203`** — Oh, you made it? *squish*... Um... *smack*... I think I'll stick to frozen pizza. But thanks.

### relationship — 2 total, 2 sampled

- **`dating_Shane`** — I... wasn't really expecting this, after all I've put you through...
- **`dating_Shane_memory_oneday`** — I think I might be the luckiest guy in the world...

### marriage — 66 total, 6 sampled

- **`patio_Shane`** — Charlie's doing well.
- **`funLeave_Shane`** — I'm going to go out today, alright?
- **`spring_23`** — Oh, right. It's the flower dance tomorrow. Hey, if it makes you happy, I'm happy.
- **`summer_1`** — I like seeing all the tropical plants this time of year. The valley gets so lush.
- **`Good_5`** — Ah... life on the farm sure beats working at Joja. That place was disgusting. You think it was depressing out front? Kid, you should've seen the back room...
- **`Rainy_Night_0`** — Hmm... seems like a good night to microwave a few pizza rolls. Some people like to cook them in the oven, but it just takes too long for me. Plus I like that squishy texture.

### callback — 3 total, 3 sampled

- **`eventSeen_611944_memory_oneweek`** — Have you tried the new Joja Bubblerito? I ate two in one sitting yesterday, that was a mistake...
- **`eventSeen_3910975`** — Sorry you had to see me like that, ...
- **`eventSeen_3910975_memory_oneweek`** — I'm trying to cut back on the drinks... it's not going to be easy.

### event — 88 total, 6 sampled

- **`event:Forest:3910975`** — ...
- **`event:Town:3917585`** — ...
- **`event:Farm:2128292`** — Uh... So I got two tickets to the Tunnelers game tonight.
- **`event:AnimalShop:3910674`** — Hopefully I won't be around long enough to need a 'plan'...
- **`event:Saloon:wewereworried`** — I'm your husband... you should trust me. I've always been honest with you about my problems. Look... I know I haven't been able to quit cold turkey... but, I'm trying my best... and I'm getting a lot healthier. My life is better now than it's ever been. I'm not in such a dark place anymore...
- **`event:Forest:3910975`** — I... I'm sorry...*hic* ... M... My life... It's a pathetic joke... Look at me... ... Why do I even try? ...*sob* I'm too small and stupid to... to take control of my life... I'm just a p... piece of soiled garbage flittering in the wind... *bluurp* ......... I've been coming here often lately... looking down... Here's a chance to finally take control of my life... These cliffs... ... B... bu... *blaap*... but I'm too scared, too anxious. Just like always...
