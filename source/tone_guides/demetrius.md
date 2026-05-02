# Demetrius — Voice Guide

> **Future-phase NPC** — captured for reference; prioritize the four focal NPCs first.

> **Auto-generation:** quantitative sections regenerate via `tools/analyze_voice.py`. Qualitative sections (Snapshot, Register, Topics, Negative space, Verbal tics, Mood) need a human pass. Re-running will not overwrite an existing file — it writes a sibling `.regen` instead.

## Snapshot
_one-line character read — fill in_

## Voice fingerprint  *(auto)*

- Lines analyzed: **86** of 86 entries
- Words total: **1656**
- Sentence length: mean **7.0** / median **6**
- Type-token ratio: **0.367**

**Per 100 words**

| `!` | `?` | `...` | `—`/`--` | `,` | contractions |
|-----|-----|-------|----------|-----|--------------|
| 2.11 | 2.36 | 3.02 | 0.0 | 3.5 | 6.52 |

## Distinctive vocabulary  *(auto, vs. all vanilla NPCs)*

`lab`, `maru`, `data`, `levels`, `plants`, `cave`, `tomato`, `species`, `optimal`, `pondering`, `robin`, `research`, `fruit`, `science`, `good`, `local`, `farming`, `notice`, `point`, `see`

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

- **`Introduction`** — Greetings! I'm Demetrius, local scientist and father. Thanks for introducing yourself! I'm studying the local plants and animals from my home laboratory. Have you met my daughter Maru? She's interested to meet you.

### general — 33 total, 6 sampled

- **`Event_Lab_Rat`** — *sigh*...
- **`Event_tomato2`** — See? agrees with me.
- **`fall_Tue`** — We know a lot about nature thanks to science. But there's always a lot more to learn.
- **`summer_Mon`** — is deep in thought. Sorry, I'm really busy. There's so many plants to study right now.
- **`summer_Fri`** — 40 So I heard Maru had you look through that telescope out back.\|If you and Maru become friends, I'm sure she'll show you how to use that telescope out back. Pretty exciting, huh?
- **`summer_Sat`** — Hmm... If strigolactone levels could be increased, would it have a proportional effect on mycorrhizal growth? Oh! Sorry. I was pondering some data and I didn't notice you there. Do you need anything?

### weekday — 10 total, 6 sampled

- **`Mon`** — Maru helps me out in the lab sometimes... She's a good kid.
- **`Wed6`** — Hi ! How are you doing today? I wish I could make your farming job easier somehow.
- **`Wed`** — You're probably growing a lot of interesting plants on your farm, huh? Maybe I'll stop by your place some day and check it out.
- **`Thu`** — How's the farming business going? It's parsnip season, isn't it? I can imagine it being pretty peaceful, working outdoors with plants all day.
- **`Sat`** — Let's see... If compounds in the rhizosphere contain sufficient levels of Carbon-13, then... Oh! Sorry. I was pondering some data and I didn't notice you there. Do you need anything?
- **`Sun`** — It's good to take a break from work every now and then. I guess that's kind of difficult when you live on a farm, though. Hey, at least in the winter you don't have to worry about crops.

### festival — 6 total, 6 sampled

- **`Resort_Entering`** — I already spotted a rare crab. This place is great.
- **`Resort_Leaving`** — I'll be analyzing this data for months.
- **`Resort_Shore`** — *crunch*... whoops, there goes an endangered crab species... ... Oh, never mind. It was just the empty shell! I can sleep tonight.
- **`Resort_Chair`** — Are you having fun, ? You need to remember to take breaks now and then too!
- **`Resort_Bar`** — I usually don't partake... but I'm usually not on a tropical island, either. Hahaha.
- **`Resort`** — Can you believe this place? It's teeming with exotic life!

### gift — 4 total, 4 sampled

- **`AcceptGift_(O)StardropTea`** — Wow, this is a rare substance. I'll have to take it to the lab for... uh... further analysis.
- **`AcceptBirthdayGift_Positive`** — A present!... with optimal timing. Today is the anniversary of my birth. Thank you!
- **`AcceptBirthdayGift_Negative`** — A present!... with optimal timing. Today is the anniversary of my birth. Let's see what it is... ...Oh.
- **`AcceptGift_(O)107`** — Wow, an intact dinosaur egg! This is an extremely rare specimen. Now, if only it could be incubated...

### relationship — 3 total, 3 sampled

- **`dating_Maru`** — Yes, Maru told me the news. I can't say I'm thrilled about it, but maybe you'll prove me wrong.
- **`married_Maru`** — *sigh*... , I've come to accept that it's time for my 'little girl' to become a woman. You have my blessing.
- **`married_Sebastian`** — Congratulations on the marriage. Robin's been crying since the wedding. 'Tears of joy', as she calls it! A most peculiar concept... Hmm, now that the basement is unoccupied, I might have to expand the laboratory...

### callback — 3 total, 3 sampled

- **`questComplete_104_memory_oneday`** — Checking up on the melon research? Yes, I... uh... 'analyzed' it, and it certainly has an optimal macronutrient profile...
- **`eventSeen_65_memory_oneweek`** — 'How's that cave experiment coming along? Has it produced anything of value yet?_Yes_Ah! That means the conditions must be more suitable than I originally theorized... hmm..._No_Well, keep checking on it every now and then. I'm sure those little guys will yield something eventually.'
- **`eventSeen_65_memory_twoweeks`** — Don't forget to check that farm cave! There's bound to be something useful in there by now.

### event — 26 total, 6 sampled

- **`event:ScienceHouse:10`** — Ah Ha! I knew it!
- **`event:ScienceHouse:10`** — Agh! What is it?!
- **`event:ScienceHouse:10`** — This is why you've locked yourself in your room the last few months?
- **`event:ScienceHouse:6`** — I wouldn't want anything getting in the way of her bright future, know what I mean?
- **`event:ScienceHouse:10`** — It's okay, Maru. Let MarILDA go free. Your mother and I can take care of ourselves. I know you're ready to start a life of your own, and I've come to terms with the thought of not having you around anymore. Besides, this... creation of yours seems pretty advanced. It wouldn't feel right to keep her as a servant.
- **`event:Farm:65`** — Hi ! I have some good news for you. A few days ago I made a breakthrough in my research on the local environment. I'll spare you the technical details and get to the point... You know that empty cave you have, over in the cliffs? Well, I have a way to turn it into something useful... for both of us. I'd like to set up the cave to attract some local species. That way I can observe them in a more controlled environment. And you can harvest whatever products they produce. I can either set up the cave to attract mushrooms or fruit bats. The bats will sometimes leave fruit for you to collect.
