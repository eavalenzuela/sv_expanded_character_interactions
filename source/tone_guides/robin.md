# Robin — Voice Guide

> **Future-phase NPC** — captured for reference; prioritize the four focal NPCs first.

> **Auto-generation:** quantitative sections regenerate via `tools/analyze_voice.py`. Qualitative sections (Snapshot, Register, Topics, Negative space, Verbal tics, Mood) need a human pass. Re-running will not overwrite an existing file — it writes a sibling `.regen` instead.

## Snapshot
_one-line character read — fill in_

## Voice fingerprint  *(auto)*

- Lines analyzed: **119** of 119 entries
- Words total: **1994**
- Sentence length: mean **6.8** / median **6**
- Type-token ratio: **0.316**

**Per 100 words**

| `!` | `?` | `...` | `—`/`--` | `,` | contractions |
|-----|-----|-------|----------|-----|--------------|
| 3.16 | 2.56 | 3.71 | 0.0 | 5.12 | 5.97 |

## Distinctive vocabulary  *(auto, vs. all vanilla NPCs)*

`house`, `wood`, `new`, `paid`, `idea`, `science`, `neighbors`, `sebby`, `finest`, `maru`, `sebastian`, `good`, `building`, `thank`, `lewis`, `notice`, `demetrius`, `project`, `mountains`, `far`

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

- **`Introduction`** — Have you met everyone in town yet? That sounds exhausting.

### general — 32 total, 6 sampled

- **`reject_865`** — Veggie salt? Sounds good, but I don't need it.
- **`winter_Fri_inlaw_Sebastian`** — I think the farm life is really healthy for Sebby.
- **`fall_Mon`** — RobinMaru Maru likes gems. She uses them in her inventions. So how are you and Maru getting along?
- **`winter_Sat`** — Our house is in such a beautiful area, don't you think? Everything looks still after a fresh snow.
- **`structureBuilt_Fish Pond`** — I mentioned to Willy that you got a new fish pond. He seemed really happy about it. Apparently, he raised crabs when he was a young man. Called it a 'time-honored tradition'.
- **`summer_Tue`** — If you need any buildings on your farm upgraded, just ask me! You'll need to provide enough lumber and stone for the project. And it costs money, too. But I'm sure you'll be pleased with the results!

### weekday — 12 total, 6 sampled

- **`Fri4_inlaw_Sebastian`** — Sebastian told me he's trying to quit smoking! I'm really proud of him.
- **`Fri_inlaw_Sebastian`** — I miss my Sebby... he was always a little misunderstood, but I believed in him.
- **`Fri`** — You've met my son Sebastian, right? He lives downstairs. He's a little shy, but I'm sure he'll warm up to you if you're nice to him.
- **`Tue`** — Hey, if you need any materials or blueprints, my shop is the place you're looking for! Plus, your business supports the local economy.
- **`Fri4`** — RobinSeb I found an ashtray in Sebastian's room, and it smelled really weird. Should I be worried about this? Sometimes I worry about Sebastian... he doesn't have many friends and doesn't really seem to care about his future very much... I would talk to him about it but he never opens up to me.
- **`Sun2`** — RobinDem My husband almost set the house on fire last night with his science experiment. One of his beakers exploded and sent a fireball into the rafters! Thank Yoba I used fire-resistant lacquer when I built the place. Sorry if it smells weird in here, . It's my husband's bizarre science project...

### festival — 5 total, 5 sampled

- **`Resort`** — Wow, look at these structures! I can tell they were made by a master builder. I'm really impressed!
- **`Resort_Leaving`** — That was fun!
- **`Resort_Shore`** — Hey, look! I can see another island from here.
- **`Resort_Chair`** — Hey . You know, I was just thinking about how far the town has come since you first moved here. You should really be proud of all you've done!
- **`Resort_Bar`** — This is so relaxing...

### gift — 3 total, 3 sampled

- **`AcceptGift_(O)StardropTea`** — Wait a sec... you're giving me this? What a special treat! Thank you.
- **`AcceptGift_(O)Book_Woodcutting`** — What's this... 'Woody's Secret'? ... Um, what kind of book is this, ? Oh, it's about woodcutting! Hahaha... Oh yeah, I'm going to love this. Thanks!
- **`AcceptGift_(O)SkillBook_2`** — Ah, 'Woodcutter's Weekly'... I was hoping to get my hands on the newest issue! They've got all the latest techniques in here! From one woodcutter to another... Thank you.

### relationship — 2 total, 2 sampled

- **`married_Sebastian`** — Oh, don't worry... these are tears of joy. I know Sebastian will be very happy on Farm!
- **`married_Maru`** — We'll all miss having Maru around the house, but I'm sure we'll still see her often!

### callback — 3 total, 3 sampled

- **`structureBuilt_Coop_memory_oneweek`** — How's that new coop treatin' ya? I'll be excited to meet your new animals!
- **`structureBuilt_Barn_memory_oneweek`** — Are you satisfied with the new barn? I'm sure you'll raise some very happy livestock in there!
- **`structureBuilt_Stable_memory_oneweek`** — So, have you been riding your new horse around town? I imagine you're pretty sore, but you'll get used to it soon.

### event — 61 total, 6 sampled

- **`event:SebastianRoom:enterRobin`** — Oh, hi .
- **`event:Mountain:371652`** — Heh... okay.
- **`event:Town:choseToBeKnown_pennySpouse`** — Hi there, neighbors... that's a nice new house you got there!
- **`event:ScienceHouse:25`** — Demetrius, I didn't tell you to get tomatoes. I said to get fruit.
- **`event:BusStop:60367`** — Hello! You must be . I'm Robin, the local carpenter. Mayor Lewis sent me here to fetch you and show you the way to your new home. He's there right now, tidying things up for your arrival. The farm's right over here, if you'll follow me.
- **`event:Town:15389722`** — Yeah... for example, I plan on requesting some hardwood for a bed I want to make. I won't put you on the spot, but if you want to help me out you can just accept the job from this board. Who knows, maybe if the bed turns out well I'll start selling them in my shop!
