# Clint — Voice Guide

> **Future-phase NPC** — captured for reference; prioritize the four focal NPCs first.

> **Auto-generation:** quantitative sections regenerate via `tools/analyze_voice.py`. Qualitative sections (Snapshot, Register, Topics, Negative space, Verbal tics, Mood) need a human pass. Re-running will not overwrite an existing file — it writes a sibling `.regen` instead.

## Snapshot
_one-line character read — fill in_

## Voice fingerprint  *(auto)*

- Lines analyzed: **83** of 83 entries
- Words total: **1474**
- Sentence length: mean **6.3** / median **5**
- Type-token ratio: **0.371**

**Per 100 words**

| `!` | `?` | `...` | `—`/`--` | `,` | contractions |
|-----|-----|-------|----------|-----|--------------|
| 1.09 | 1.97 | 5.09 | 0.0 | 4.68 | 6.38 |

## Distinctive vocabulary  *(auto, vs. all vanilla NPCs)*

`blacksmith`, `tools`, `upgrade`, `furnace`, `advice`, `emily`, `mon`, `pickaxe`, `bars`, `women`, `date`, `grandfather`, `work`, `act`, `gulp`, `also`, `anything`, `sigh`, `father`, `event`

## Register
- Default: 
- With trusted player: 
- Under stress / when annoyed: 

## Topics they pursue
- 

## Topics they avoid / deflect
- 

## Lines they would never say  *(negative space)*
- 

## Verbal tics / pet phrases
- 

## Mood shifts (preview for Phase 3)
- Happy: 
- Tired/down: 
- Annoyed: 

## Sample lines by category  *(auto)*

### intro — 1 total, 1 sampled

- **`Introduction`** — Er... hi. I'm Clint. I'm the town blacksmith. If you ever need to upgrade your tools, I'm your guy.

### general — 10 total, 6 sampled

- **`event_advice1`** — Okay... I'll keep that in mind.
- **`divorced_Emily`** — I've been feeling strangely hopeful lately.
- **`reject_868`** — Hmm... That's an interesting stone, like nothing I've ever seen before. I wouldn't know what to do with it, though. I deal in the mundane, not the magical...
- **`mineArea_121`** — Interesting. There's tiny iridium flakes on your pickaxe... you've been going to the desert caves, huh? I've always wanted to smelt with iridium. It's not easy to come by.
- **`cc_Minecart`** — Somehow, the old town minecart system started working again. It's very convenient for getting to and from the mines. Don't get too cozy, though... if it can start up so suddenly, it could just as well shut down...
- **`GreenRain_2`** — I feel bad admitting it, but sometimes I wish there was a real disaster, not just some dumb green rain. Something to shake everything up, you know? Not that I want people to get hurt... I just want to feel alive... To feel like I have a purpose...

### weekday — 20 total, 6 sampled

- **`Mon_9`** — How'd you know?
- **`Mon_clown`** — Hahahaha. Good one.
- **`Thu8`** — I heard Emily has a friend who lives in the desert. Do you know anything about her? I wonder if she's single...
- **`Sat10`** — How are your tools holding up? If they ever need repairs, just come by my shop. I guarantee these tools for life!
- **`Sun8`** — I don't know if people realize this, or care, but I do take a lot of pride in my work. I mean... When I was a boy I didn't really dream of becoming a blacksmith. But that's what I am. And I want to be the best blacksmith I can be.
- **`Mon`** — Yep. I'm a blacksmith. My father was also a blacksmith. My grandfather was a blacksmith as well. 9/9 Mon_old I bet you can't guess what my great-grandfather was... 9 30 Mon_9 A blacksmith. 9 50 Mon_clown A silly clown. 9 -50 Mon_rude A sarcastic jerk.

### festival — 7 total, 6 sampled

- **`Resort_Bar`** — I'm hungry...
- **`Resort_Shore`** — Oh no... I forgot to clip my toenails.
- **`Resort_Leaving`** — Well, that didn't turn out like I was imagining...
- **`Resort`** — *sigh*... We're all at the beach but I still feel so alone...
- **`Resort_Entering`** — I'm gonna put on my special red trunks. They're supposed to be really eye-catching.
- **`Resort_Shore_2`** — I thought working a furnace would have prepared me for this heat, but I'm sweating in places I didn't know I could. I hope no one noticed... 's body is glistening...

### gift — 4 total, 4 sampled

- **`AcceptBirthdayGift_Positive`** — I don't usually get birthday gifts. This actually means a lot, . Thank you.
- **`AcceptBirthdayGift_Negative`** — Is this a birthday gift? It's, uh... an interesting choice. Well I appreciate that you remembered me, anyway.
- **`AcceptGift_(O)StardropTea`** — You're giving this... to me? I don't think I deserve it, but.. thank you.
- **`AcceptGift_(O)SkillBook_3`** — Oh, interesting... These books aren't very easy to come by in the valley. Looks like there's a lot of good tips in here. Thanks, .

### relationship — 2 total, 2 sampled

- **`dating_Emily`** — I... um... heard that you and Emily are together. Congratulations.
- **`married_Emily`** — is looking at the ground and won't say anything to you.

### callback — 1 total, 1 sampled

- **`eventSeen_101_memory_oneweek`** — Did Emily say anything about our date the other day? Wait, don't tell me... I'm better off not knowing. Maybe I can still salvage my dignity.

### event — 38 total, 6 sampled

- **`event:Saloon:97`** — Yes!
- **`event:Town:831125`** — I'm sorry!
- **`event:Town:101`** — I was wondering if you'd go w... with... tomorrow, me... *gulp*
- **`event:Saloon:97`** — Er.. I mean, I'll have the Big n' Cheesy. With extra sauce, please. ...
- **`event:Saloon:97`** — 211 null Got any tips?^What advice can you give me? 211 25 event_advice1 Impress women with your strength and charm 211 25 event_advice1 Act crazy, to keep people guessing 211 0 event_advice2 Just act natural... be yourself 211 25 event_advice1 Treat women the same as men
- **`event:Town:831125`** — Have no fear, my dear. The world-class science team at Joja Headquarters have determined that 'Joja Bluu' does not cause a significant erosion of the stomach lining. So you can drink it whenever you like, as much as you like. The real question is... 'When will YOU turn bluu?'... *glug* *glug*... Ahh...
