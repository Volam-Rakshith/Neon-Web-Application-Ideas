#!/usr/bin/env python3
"""Mystery Deck idea engine -> 500 grammatical, distinct web-app ideas."""
import json, random, re
from collections import Counter

random.seed(1337)

CATS = ["AI & Copilots","Social","Productivity","Health","Mind & Mood","Creative","Music & Audio",
        "Dev Tools","Learning","Money & Work","Food & Drink","Outdoors","Home & Life","Play & Games"]

AUD = {
 "AI & Copilots":["indie founders","solo developers","research assistants","support teams","freelance writers","prompt hoarders"],
 "Social":["long-distance couples","group chats that never sleep","roommates","alumni crews","new-in-town transplants","families across time zones"],
 "Productivity":["remote teams","freelancers with six clients","grad students","night-shift workers","one-person startups","overbooked parents"],
 "Health":["marathon rookies","physio patients","chronic-illness warriors","new parents","climbing gym regulars","people who hate the gym"],
 "Mind & Mood":["anxious overthinkers","ADHD brains","therapy goers","burnt-out caretakers","insomniacs","people learning to sit still"],
 "Creative":["illustrators","zine makers","film photographers","type designers","tattoo artists","worldbuilders"],
 "Music & Audio":["session musicians","bedroom producers","podcast editors","choir directors","buskers","DJs with too many crates"],
 "Dev Tools":["open-source maintainers","junior devs","platform teams","hackathon crews","solo SaaS builders","reviewers on deadline"],
 "Learning":["language learners","PhD candidates","homeschool parents","ESL teachers","career switchers","exam cram crews"],
 "Money & Work":["gig drivers","Etsy sellers","contractors","first-job twenty-somethings","market vendors","creators with irregular income"],
 "Food & Drink":["weeknight cooks","sourdough obsessives","home brewers","meal preppers","picky-eater households","coffee nerds"],
 "Outdoors":["urban beekeepers","birdwatchers","mushroom foragers","community gardeners","backpackers","balcony growers"],
 "Home & Life":["dog trainers","aquarium keepers","HOA boards","people who lose every manual","thrifters","plant parents"],
 "Play & Games":["dungeon masters","board-game cafés","speedrunners","trivia nights","escape-room designers","cosplayers"],
}
GEN_WHO = ["you and three friends","two-person teams","people with one lunch break","entire group chats",
           "strangers with one shared obsession","communities of six","phone-only people","desktop die-hards",
           "sibling duos","four coworkers who became friends","couples in different cities","retirees with time to burn"]

# (plural subject, short modifier, category)
S = [
 ("sourdough starters","Starter","Food & Drink"),("houseplant cuttings","Cutting","Home & Life"),
 ("vinyl records","Vinyl","Music & Audio"),("thrifted denim","Denim","Money & Work"),
 ("mechanical keyboards","Keeb","Dev Tools"),("board game collections","BoardGame","Play & Games"),
 ("D&D campaigns","Campaign","Play & Games"),("running routes","Route","Health"),
 ("bouldering problems","Problem","Health"),("cold plunge sessions","Plunge","Health"),
 ("sleep schedules","Sleep","Mind & Mood"),("dreams worth remembering","Dream","Mind & Mood"),
 ("fridge leftovers","Leftover","Food & Drink"),("pour-over coffee","PourOver","Food & Drink"),
 ("loose-leaf tea blends","Tea","Food & Drink"),("cocktail experiments","Cocktail","Food & Drink"),
 ("Sunday meal prep","MealPrep","Food & Drink"),("grocery runs","Grocery","Food & Drink"),
 ("wine and cheese pairings","Pairing","Food & Drink"),("home fermentation jars","Ferment","Food & Drink"),
 ("compost bins","Compost","Outdoors"),("balcony gardens","Balcony","Outdoors"),
 ("bird sightings","Bird","Outdoors"),("tide charts","Tide","Outdoors"),
 ("backyard stargazing","Stargazing","Outdoors"),("35mm film rolls","Film","Creative"),
 ("darkroom scans","Darkroom","Creative"),("handmade zines","Zine","Creative"),
 ("daily sketchbooks","Sketchbook","Creative"),("pixel art sprites","Sprite","Creative"),
 ("shader experiments","Shader","Creative"),("typefaces found in the wild","Type","Creative"),
 ("color palettes","Palette","Creative"),("moodboards","Mood","Creative"),
 ("flash fiction","Fiction","Creative"),("poems worth keeping","Poem","Creative"),
 ("half-finished songs","Demo","Music & Audio"),("beat sketches","Beat","Music & Audio"),
 ("sample packs","Sample","Music & Audio"),("podcast episodes","Podcast","Music & Audio"),
 ("voice memos","Memo","Music & Audio"),("guitar tabs","Tab","Music & Audio"),
 ("metronome practice","Metronome","Music & Audio"),("piano scales","Scale","Music & Audio"),
 ("foreign-language vocabulary","Vocab","Learning"),("flashcard decks","Flashcard","Learning"),
 ("messy lecture notes","Lecture","Learning"),("dense research papers","Paper","Learning"),
 ("citations and bibliographies","Citation","Learning"),("thesis chapters","Thesis","Learning"),
 ("job applications","Job","Money & Work"),("résumés","Resume","Money & Work"),
 ("interview questions","Interview","Money & Work"),("salary conversations","Salary","Money & Work"),
 ("side hustles","Hustle","Money & Work"),("freelance invoices","Invoice","Money & Work"),
 ("client contracts","Contract","Money & Work"),("forgotten subscriptions","Subscription","Money & Work"),
 ("envelope budgets","Budget","Money & Work"),("savings goals","Savings","Money & Work"),
 ("therapy homework","Therapy","Mind & Mood"),("medication reminders","Dose","Health"),
 ("symptom logs","Symptom","Health"),("physio exercise sets","Physio","Health"),
 ("morning mobility routines","Mobility","Health"),("yoga sequences","Yoga","Health"),
 ("breathing drills","Breath","Mind & Mood"),("migraine triggers","Migraine","Health"),
 ("allergy seasons","Allergy","Health"),("menstrual cycles","Cycle","Health"),
 ("baby feeding windows","Feeding","Home & Life"),("toddler tantrums","Tantrum","Home & Life"),
 ("homeschool weeks","Homeschool","Learning"),("kids' chores and allowance","Chore","Home & Life"),
 ("pet vaccination dates","PetVax","Home & Life"),("dog walks","Walk","Home & Life"),
 ("cat behavior quirks","CatQuirk","Home & Life"),("aquarium water parameters","Aquarium","Home & Life"),
 ("reptile enclosure humidity","Reptile","Home & Life"),("chicken coop logs","Coop","Outdoors"),
 ("mushroom grows","Mushroom","Outdoors"),("home brew batches","Homebrew","Food & Drink"),
 ("cheese caves","Cave","Food & Drink"),("candle pours","Candle","Money & Work"),
 ("pottery wheels","Pottery","Creative"),("theatre rehearsals","Theatre","Play & Games"),
 ("improv scenes","Improv","Play & Games"),("stream overlays","Overlay","Dev Tools"),
 ("VTuber rig presets","Rig","Creative"),("cosplay builds","Cosplay","Creative"),
 ("escape room puzzles","EscapeRoom","Play & Games"),("museum artifacts","Artifact","Learning"),
 ("science explainers","Explainer","Learning"),("mutual-aid requests","MutualAid","Social"),
 ("neighborhood tools","Borrow","Social"),("book club picks","BookClub","Social"),
 ("running club stats","Club","Health"),("open-source issue queues","Issue","Dev Tools"),
 ("pull request reviews","PR","Dev Tools"),("API playgrounds","API","Dev Tools"),
 ("regex one-liners","Regex","Dev Tools"),("SQL queries","SQL","Dev Tools"),
 ("git commit habits","Commit","Dev Tools"),("deploy pipelines","Deploy","Dev Tools"),
 ("incident postmortems","Postmortem","Dev Tools"),("standup updates","Standup","Productivity"),
 ("deep work blocks","DeepWork","Productivity"),("browser tab hoards","Tab","Productivity"),
 ("meeting notes","Minutes","Productivity"),("inbox triage","Inbox","Productivity"),
 ("unfinished reading lists","Reading","Learning"),("article highlights","Highlight","Learning"),
 ("podcast timestamps","Timestamp","Music & Audio"),("conference talks","Talk","Learning"),
 ("prompt libraries","Prompt","AI & Copilots"),("model evals","Eval","AI & Copilots"),
 ("RAG document sets","Corpus","AI & Copilots"),("AI art generations","AIArt","AI & Copilots"),
 ("chat transcripts worth saving","Transcript","AI & Copilots"),("fine-tuning datasets","Dataset","AI & Copilots"),
 ("agent tool configs","Agent","AI & Copilots"),("hallucination catches","Factcheck","AI & Copilots"),
 ("group gift funds","GiftFund","Social"),("wedding seating charts","Seating","Social"),
 ("travel itineraries","Itinerary","Social"),("airport layovers","Layover","Outdoors"),
 ("hostel bunk swaps","Hostel","Social"),("camping gear","Gear","Outdoors"),
 ("fishing spots","Fishing","Outdoors"),("surf forecasts","Surf","Outdoors"),
 ("skate spots","Skate","Outdoors"),("street photography walks","PhotoWalk","Creative"),
 ("vintage camera repairs","Camera","Home & Life"),("bike maintenance","Bike","Home & Life"),
 ("car service history","Car","Home & Life"),("tool libraries","ToolLibrary","Home & Life"),
 ("seed swaps","Seed","Outdoors"),("cut flower gardens","CutFlower","Outdoors"),
 ("weekend bakes","Bake","Food & Drink"),("hot sauce experiments","HotSauce","Food & Drink"),
 ("coffee cupping notes","Cupping","Food & Drink"),("tea aging shelves","Aging","Food & Drink"),
 ("restaurant secret menus","SecretMenu","Food & Drink"),("street food stalls","StreetFood","Food & Drink"),
 ("night markets","NightMarket","Money & Work"),("flea market finds","Flea","Money & Work"),
 ("estate sale picks","Estate","Money & Work"),("record store digs","Digger","Music & Audio"),
 ("synth patch libraries","Patch","Music & Audio"),("drum machine kits","DrumKit","Music & Audio"),
 ("lyric notebooks","Lyric","Music & Audio"),("open mic lineups","OpenMic","Music & Audio"),
 ("choir sheet music","Score","Music & Audio"),("practice room bookings","RoomBooking","Music & Audio"),
 ("gig setlists","Setlist","Music & Audio"),("merch drops","Merch","Money & Work"),
 ("newsletter archives","Archive","Creative"),("manga reading orders","Manga","Play & Games"),
 ("anime watch lists","Anime","Play & Games"),("fan translation credits","Fansub","Play & Games"),
 ("retro game saves","SaveState","Play & Games"),("emulator configs","Emulator","Play & Games"),
 ("speedrun splits","Speedrun","Play & Games"),("trivia question banks","Trivia","Play & Games"),
 ("pub quiz teams","PubQuiz","Play & Games"),("chess openings","Chess","Play & Games"),
 ("poker hand histories","Hand","Play & Games"),("fantasy league drafts","Fantasy","Play & Games"),
 ("youth sports rotations","Rotation","Health"),("pick-up basketball runs","Pickup","Health"),
 ("climbing beta","Send","Health"),("marathon training blocks","Training","Health"),
 ("desk stretches","Stretch","Health"),("posture checks","Posture","Health"),
 ("hydration nudges","Water","Health"),("caffeine cutoffs","Caffeine","Health"),
 ("step count bets","Steps","Health"),("gratitude prompts","Gratitude","Mind & Mood"),
 ("panic attack playbooks","Panic","Mind & Mood"),("grief anniversaries","Grief","Mind & Mood"),
 ("sober-day counters","Sober","Mind & Mood"),("digital detox pacts","Detox","Mind & Mood"),
 ("journal prompts for people who don't journal","Journal","Mind & Mood"),
 ("relationship check-ins","Checkin","Social"),("friendship maintenance","Friendship","Social"),
 ("long-distance date nights","DateNight","Social"),("family recipe archives","Heirloom","Food & Drink"),
 ("grandparent oral histories","Oral","Social"),("baby name shortlists","BabyName","Home & Life"),
 ("pregnancy weeks","Pregnancy","Health"),("dog training milestones","DogTraining","Home & Life"),
 ("cat adoption matching","Adoption","Social"),("animal shelter intake logs","Shelter","Social"),
 ("foster placement calendars","Foster","Social"),("lost-and-found pets","LostPet","Home & Life"),
 ("neighborhood watch rounds","Neighborhood","Social"),("community fridges","Fridge","Social"),
 ("skill swaps","Skill","Social"),("language exchange partners","Exchange","Learning"),
 ("study room focus cams","FocusCam","Learning"),("exam countdown clocks","Countdown","Learning"),
 ("internship applications","Internship","Money & Work"),("portfolio critiques","Portfolio","Creative"),
 ("freelance rate cards","Rate","Money & Work"),("client onboarding forms","Onboarding","Money & Work"),
 ("agency timesheets","Timesheet","Money & Work"),("contractor day rates","DayRate","Money & Work"),
 ("creator tax write-offs","Writeoff","Money & Work"),("royalty splits","Royalty","Music & Audio"),
 ("band practice shares","Practice","Music & Audio"),("studio session logs","Session","Music & Audio"),
 ("mix revision rounds","MixRevision","Music & Audio"),("mastering references","Mastering","Music & Audio"),
 ("playlist curations","Playlist","Music & Audio"),("radio show archives","Radio","Music & Audio"),
 ("field recordings","Field","Music & Audio"),("foley libraries","Foley","Music & Audio"),
 ("game jam submissions","GameJam","Play & Games"),("itch.io wishlists","Itchio","Play & Games"),
 ("playtest feedback forms","Playtest","Play & Games"),("bug repro steps","Repro","Dev Tools"),
 ("feature flag rollouts","Flag","Dev Tools"),("cron job graveyards","Cron","Dev Tools"),
 ("dependency audits","Deps","Dev Tools"),("database migrations","Migration","Dev Tools"),
 ("test coverage gaps","Coverage","Dev Tools"),("design system tokens","Token","Dev Tools"),
 ("component libraries","Component","Dev Tools"),("Figma handoff notes","Handoff","Dev Tools"),
 ("accessibility audits","A11y","Dev Tools"),("Lighthouse scores","Lighthouse","Dev Tools"),
 ("SEO title experiments","SEO","Dev Tools"),("landing page A/B tests","Landing","Dev Tools"),
 ("changelog posts","Changelog","Dev Tools"),("status pages","Status","Dev Tools"),
 ("uptime pings","Uptime","Dev Tools"),("log tail dashboards","Logs","Dev Tools"),
 ("cost-per-request alerts","CloudCost","Dev Tools"),("on-call rotations","Oncall","Dev Tools"),
 ("hackathon team forming","Hackathon","Dev Tools"),("student project demos","Showcase","Learning"),
 ("science fair judging","ScienceFair","Learning"),("robotics competition logs","Robotics","Learning"),
 ("math problem sets","ProblemSet","Learning"),("chemistry lab notebooks","Lab","Learning"),
 ("astronomy observation logs","Observation","Outdoors"),("weather station readings","Weather","Outdoors"),
 ("air quality readings","AirQuality","Outdoors"),("river clean-up shifts","River","Outdoors"),
 ("tree planting plots","Tree","Outdoors"),("native species maps","Native","Outdoors"),
 ("trail maintenance crews","Trail","Outdoors"),("parkrun volunteer rosters","Volunteer","Outdoors"),
 ("cycling commute routes","Commute","Outdoors"),("e-bike battery logs","Battery","Outdoors"),
 ("scooter repair shops","Scooter","Home & Life"),("3D printer profiles","Print","Dev Tools"),
 ("laser cutter settings","Laser","Creative"),("CNC toolpaths","Toolpath","Creative"),
 ("resin print failures","Resin","Creative"),("miniature painting armies","Army","Play & Games"),
 ("miniature wargame rosters","Roster","Play & Games"),("trading card collections","TCG","Play & Games"),
 ("grading slabs","Slab","Money & Work"),("sneaker restocks","Restock","Money & Work"),
 ("watch collections","Watch","Money & Work"),("fountain pen inks","Ink","Creative"),
 ("stationery hauls","Stationery","Creative"),("bullet journal spreads","Bullet","Productivity"),
 ("habit tracker grids","Habit","Productivity"),("pomodoro sessions","Pomodoro","Productivity"),
 ("weekly reviews","Weekly","Productivity"),("quarterly OKRs","OKR","Productivity"),
 ("goal-setting rituals","Ritual","Productivity"),("decision journals","Decision","Productivity"),
 ("bookmark graveyards","Bookmark","Productivity"),("read-later queues","ReadLater","Productivity"),
 ("newsletter triage","Newsletter","Productivity"),("calendar tetris","Calendar","Productivity"),
 ("travel packing lists","Packing","Social"),("visa paperwork","Visa","Social"),
 ("expat tax deadlines","ExpatTax","Money & Work"),("language immersion trips","Immersion","Learning"),
 ("study abroad housing","Abroad","Learning"),("scholarship essays","Scholarship","Learning"),
 ("student loan payoffs","Loan","Money & Work"),("first apartment checklists","Apartment","Home & Life"),
 ("moving day logistics","Moving","Home & Life"),("storage unit inventories","Storage","Home & Life"),
 ("warranty and receipt vaults","Warranty","Home & Life"),("appliance manuals","Manual","Home & Life"),
 ("home repair histories","Repair","Home & Life"),("renter's insurance claims","Claim","Money & Work"),
 ("utility bill spikes","Utility","Money & Work"),("solar panel output","Solar","Outdoors"),
 ("rainwater barrels","Barrel","Outdoors"),("EV charging sessions","Charge","Outdoors"),
 ("carbon footprint estimates","Carbon","Outdoors"),("thrift flip margins","Flip","Money & Work"),
 ("upcycling projects","Upcycle","Creative"),("repair café events","RepairCafe","Social"),
 ("clothing swap parties","ClothesSwap","Social"),("gift registry splits","Registry","Social"),
 ("birthday potlucks","Potluck","Food & Drink"),("dinner party seating","DinnerParty","Social"),
 ("recipe scaling for crowds","Scaling","Food & Drink"),("pantry inventories","Pantry","Food & Drink"),
 ("spice rack maps","Spice","Food & Drink"),("sourdough hydration math","Hydration","Food & Drink"),
 ("bake sale pricing","BakeSale","Money & Work"),("coffee subscription roasters","Roaster","Food & Drink"),
 ("tea subscription boxes","Box","Food & Drink"),("snack box reviews","Snack","Food & Drink"),
 ("energy drink rankings","EnergyDrink","Play & Games"),("hot sauce heat scales","Heat","Food & Drink"),
 ("cheese board builders","CheeseBoard","Food & Drink"),("charcuterie ratios","Ratio","Food & Drink"),
 ("fermentation safety checks","Safety","Food & Drink"),("canning seasons","Canning","Food & Drink"),
 ("root cellar stocks","Cellar","Food & Drink"),("foraging ethics rules","Foraging","Outdoors"),
 ("wild garlic patches","WildGarlic","Outdoors"),("hedgerow berry maps","Berry","Outdoors"),
 ("urban orchard trees","Orchard","Outdoors"),("guerrilla gardening spots","Guerrilla","Outdoors"),
 ("bee hive inspections","Hive","Outdoors"),("pollinator counts","Pollinator","Outdoors"),
 ("moth trapping nights","Moth","Outdoors"),("frog call surveys","Frog","Outdoors"),
 ("citizen science datasets","CitizenSci","Outdoors"),("bioblitz events","Bioblitz","Outdoors"),
]

# (mechanic noun, kind word, transitive verb, twist sentence)
M = [
 ("Barter Board","board","trade {o}","Nothing is for sale — every item is a favor you bank and spend later."),
 ("Swipe Deck","deck","swipe through {o}","Matches expire in 24 hours, so nobody hoards them."),
 ("Time Capsule","capsule","lock {o} away","Whatever you post stays sealed until a date you pick."),
 ("Streak Ladder","ladder","keep a streak on {o}","Break the chain and you drop a division. Everyone sees it."),
 ("Live Canvas","canvas","co-edit {o}","One shared surface, every cursor visible, zero merge conflicts."),
 ("Bounty Board","board","post bounties on {o}","Anyone can claim the job; payment releases on proof."),
 ("Recall Deck","deck","drill {o}","Spaced repetition decides what resurfaces and when."),
 ("AR Layer","layer","tag {o}","Point the camera and the annotations float where they belong."),
 ("Voice Journal","journal","talk through {o}","Transcribed, searchable, and it never asks you to type."),
 ("Ambient Dashboard","dashboard","watch {o}","No notifications — one calm screen that shifts color with the state."),
 ("Guild Hall","hall","rally a guild around {o}","Six to twelve people, shared goals, weekly rituals."),
 ("Daily Ritual","ritual","check in on {o}","Same three questions, every day, forever."),
 ("Slow Feed","feed","post about {o}","One update per person per day. That is the whole constraint."),
 ("24-Hour Room","room","talk about {o}","The room and everything in it deletes at midnight."),
 ("Pin Map","map","pin {o}","Discovery is geographic — you only see what is near you."),
 ("Chain Playlist","playlist","queue {o} up","Each entry must answer the one before it, like a conversation."),
 ("Mentor Match","match","get mentored on {o}","Two-way opt-in, six-week commitment, structured check-ins."),
 ("Peer Review Swap","swap","trade feedback on {o}","You cannot see notes on your own work until you review two others."),
 ("Micro-Lesson","lesson","learn {o}","Three-minute bites, no curriculum committee, just the next bite."),
 ("Quiz Duel","duel","quiz each other on {o}","Best of five, thirty seconds a question, live scoreboard."),
 ("Escape Room","puzzle room","build puzzles around {o}","A timer, a hint economy, and a leaderboard of solve times."),
 ("Prompt Engine","engine","generate prompts for {o}","Roll the dice, get ten directions, keep the one that sparks."),
 ("AI Copilot","copilot","get an AI copilot for {o}","It drafts, you decide. Nothing ships without a human tap."),
 ("Offline Kit","kit","manage {o}","Local-first by default; sync happens when a network shows up."),
 ("Browser Sidekick","sidekick","grab {o}","One keystroke, no tab switch, no login wall."),
 ("Desk Widget","widget","glance at {o}","It lives on the desktop and updates without being opened."),
 ("API Bazaar","bazaar","sell access to {o}","Metered, documented, testable right in the browser."),
 ("Data Lens","lens","visualize {o}","Same data, twelve views, one toggle between them."),
 ("Silent Auction","auction","bid on {o}","Sealed bids, all revealed at the same moment."),
 ("Remix Engine","engine","remix {o}","Every output credits its parents — the lineage tree is public."),
 ("Shared Ledger","ledger","split the cost of {o}","Everyone sees the same numbers; nobody has to ask."),
 ("Roulette","roulette","get matched on {o}","Opt in, get paired, five minutes on the clock."),
 ("Signal Tracker","tracker","track {o}","Only the interesting deltas surface, never the raw firehose."),
 ("Tournament Bracket","bracket","run a bracket on {o}","Single elimination, public seeds, brutal and fair."),
 ("Workshop","workbench","host workshops on {o}","The host sets the agenda, guests bring work, a timer keeps it honest."),
 ("Almanac","almanac","keep a year-long record of {o}","One row per day, printable at the end of the year."),
 ("Dossier","dossier","build a dossier on {o}","Everything public, everything sourced, nothing anonymous."),
 ("Cockpit","cockpit","command {o}","Keyboard-first: the common path takes zero clicks."),
 ("Forge","forge","forge {o}","Templates in, finished artifacts out, versioned automatically."),
 ("Atlas","atlas","map {o} out","Zoom from one item to the whole collection without losing context."),
 ("Kitchen Sink","kitchen sink","throw everything at {o}","Deliberately maximal — every feature ships behind a toggle."),
 ("Confessional","confessional","confess things about {o}","Anonymous by default, verified by reputation, moderated by the group."),
 ("Trading Floor","floor","swap {o}","Order-book energy applied to something gloriously mundane."),
 ("Ritual Calendar","calendar","schedule {o}","Recurring events that survive missed weeks without guilt."),
 ("Field Guide","guide","write field guides to {o}","Community-written, expert-reviewed, printable in the field."),
 ("Lab Notebook","lab","run experiments on {o}","Hypothesis, method, result — nothing gets deleted, ever."),
 ("Radio Station","station","broadcast {o}","An always-on stream with a listener queue and live requests."),
 ("Arcade","arcade","play mini-games about {o}","Thirty-second games, instant restart, no tutorial."),
 ("Sanctuary","sanctuary","slow down with {o}","No metrics, no streaks, no leaderboards. Just the thing."),
 ("War Room","war room","coordinate {o}","Everyone sees the same board; decisions get timestamped."),
 ("Scrapbook","scrapbook","scrapbook {o}","Tape, stickers, crooked captions — deliberately unpolished."),
 ("Greenhouse","greenhouse","grow {o}","Tiny daily inputs compound into something showable in a year."),
 ("Vault","vault","store {o}","Encrypted, exportable, and still readable in ten years."),
 ("Mixtape","mixtape","sequence {o}","Order matters more than content; each transition is a statement."),
 ("Chorus","chorus","harmonize on {o}","Layers stack until the group sounds bigger than anyone in it."),
 ("Favor Ledger","ledger","trade favors over {o}","Who owes whom, settled by doing rather than paying."),
 ("Corner Shop","shop","sell {o}","Three products max, restocked weekly, closed when sold out."),
 ("Observatory","observatory","observe {o}","Passive monitoring that only wakes you when the pattern breaks."),
 ("Playbook","playbook","run plays on {o}","Prebuilt sequences with checkpoints and fallback branches."),
 ("Salon","parlor","host salons on {o}","Eight seats, one topic, a moderator, a published transcript."),
]

TECH = ["WebSockets","WebRTC","CRDTs","IndexedDB","Service Workers","Web Audio API","WebGL","WebGPU",
 "Three.js","SQLite WASM","WASM","PWA","Web Share API","File System Access","Canvas 2D","Web Workers",
 "Speech-to-Text","on-device LLM","passkeys","Push API","Geolocation","WebXR","in-browser OCR",
 "vector embeddings","local-first sync","Edge Functions","Stripe","LLM API","Maps API","iCal feeds",
 "RSS parsing","Markdown","drag-and-drop","virtualized lists","offline caching","QR handoff"]

EXTRA = ["Ships as one static page and a tiny backend.","No accounts — a passkey is your login.",
 "Works offline, syncs when you reconnect.","Keyboard-driven end to end.",
 "Revenue is a single $4 unlock, never a subscription.","Phone-first, thumb-reachable UI.",
 "Every export is a plain file you own.","Launches as a waitlist and nothing else.",
 "Designed to be abandoned gracefully — the data outlives the app.","MVP is a weekend; the moat is the community.",
 "Print stylesheet included, because paper still wins.","No dark patterns, no infinite scroll."]

KEEP = {"AI","API","AR","SQL","SEO","OKRs","A11y","3D","35mm","D&D","EV","RAG","LLM","VTuber","Etsy",
        "Figma","Hoard","Lighthouse","QR","TCG","itch.io","parkrun","e-bike","HOA","ESL","PhD","PWA",
        "Résumés","A/B","CNC","CSS","MVP","PR"}

CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
NOSPLIT = {"VTuber"}
def disp(mod):
    if mod in NOSPLIT: return mod
    return " ".join(CAMEL.split(mod))

SMALL = {"a","an","the","of","for","with","on","in","to","and","or","at","by","from"}
def tc(phrase):
    out = []
    for w in phrase.split(" "):
        core = w.strip(".,:;()—'")
        if core in KEEP or w in KEEP: out.append(w); continue
        if any(ch.isdigit() for ch in w): out.append(w); continue
        if core.lower() in SMALL and out:
            out.append(core.lower()+ (w[len(core):] if len(w)>len(core) else "")); continue
        if "-" in w:
            out.append("-".join(p[:1].upper()+p[1:] if p else p for p in w.split("-")))
        else:
            out.append(w[:1].upper()+w[1:])
    return " ".join(out)

VOW = set("aeiou")
def art(noun):
    n = noun.lstrip().lower()
    return "an" if (n[:1] in VOW) else "a"

PREP = {"on","of","to","at","through","around","about","with","for","over","up","out","away","in","into","by"}
def iv(v):
    """verb usable as a punchy imperative title, else None"""
    p = " ".join(v.replace("{o}","").split())
    w = p.split(" ")
    if len(w) > 2 or w[-1].lower() in PREP: return None
    return p

def cap(p): return p[:1].upper()+p[1:]

# ------------------------------------------------------- handcrafted flags
FLAGSHIP = [
 ("Idea Graveyard","AI & Copilots",3,"An archive where dead startup ideas get resurrected, remixed and voted back to life by strangers who were not there the first time.",["LLM API","Markdown","virtualized lists"]),
 ("Taste Graph","Creative",4,"Rate 200 images and the app builds a map of your aesthetic, then finds other people standing in the same corner of it.",["vector embeddings","WebGL","Canvas 2D"]),
 ("Fridge Forager","Food & Drink",2,"Photograph the inside of your fridge; get three recipes you can actually make tonight without shopping.",["in-browser OCR","LLM API","PWA"]),
 ("Silent Bookclub","Learning",2,"Everyone reads the same chapter on the same night, cameras on, microphones off, then one shared note wall afterwards.",["WebRTC","Markdown","iCal feeds"]),
 ("Split the Sky","Outdoors",3,"A live map of who is looking at which patch of sky right now, so amateur astronomers can co-observe the same transient event.",["WebSockets","Maps API","Geolocation"]),
 ("Debt Snowball Club","Money & Work",3,"Anonymous accountability pods of five people paying down debt together, with a shared progress bar and zero financial advice.",["SQLite WASM","passkeys","Push API"]),
 ("Sound of My Street","Music & Audio",4,"Drop a pin, record ten seconds; the city slowly fills with an ambient map of what every block sounds like at 7am.",["Web Audio API","Geolocation","IndexedDB"]),
 ("Standup Roulette","Dev Tools",2,"Async standups that pair you with one random teammate each morning for a two-minute voice exchange instead of a channel dump.",["Speech-to-Text","WebSockets","Push API"]),
 ("Grief Calendar","Mind & Mood",3,"Quietly schedules support around anniversaries and firsts, and nudges the friends who said 'let me know if you need anything'.",["iCal feeds","Push API","local-first sync"]),
 ("Beta Reader Exchange","Creative",2,"Swap manuscript chapters with matched readers; structured feedback forms replace the dreaded 'it was good'.",["Markdown","CRDTs","passkeys"]),
 ("Plant ER","Home & Life",2,"Snap a dying leaf, get a triage queue: water, light, pests, or 'it is already gone'. Community botanists confirm the diagnosis.",["in-browser OCR","LLM API","Push API"]),
 ("Rehearsal Room","Music & Audio",3,"A shared metronome, click track and setlist that every band member's device stays locked to, even in different rooms.",["WebRTC","Web Audio API","WebSockets"]),
 ("Tool Lender","Social",2,"Neighborhood inventory of drills, ladders and pressure washers with a deposit-free trust score and a handoff QR code.",["QR handoff","Geolocation","PWA"]),
 ("Chore Wars","Home & Life",1,"Roommates bid on chores in an economy of points that convert into choosing Friday's dinner.",["SQLite WASM","Push API","drag-and-drop"]),
 ("Cold Open","Play & Games",4,"Improv troupes run scenes over video with a prompt deck, a shot clock and an audience that votes with one key.",["WebRTC","WebSockets","Web Audio API"]),
 ("Field Notes Offline","Outdoors",3,"A fully offline naturalist journal with species packs, GPS tracks and sketch layers that sync only when you're back in town.",["Service Workers","IndexedDB","Geolocation"]),
 ("Price Whisperer","Money & Work",3,"Paste any freelancer's rate card and see a live distribution of what comparable people actually charge, anonymously.",["vector embeddings","Edge Functions","Stripe"]),
 ("Loop Pedal for Writers","Creative",2,"A writing sprint app where your paragraph gets remixed by the next writer in the chain, and you only see the original at the end.",["CRDTs","Markdown","WebSockets"]),
 ("Sleeve Notes","Music & Audio",2,"Scan any vinyl sleeve and add your own liner notes to a shared, growing archive of fan-written history.",["in-browser OCR","Markdown","RSS parsing"]),
 ("Quiet Hours","Mind & Mood",1,"A group pact app: everyone's phone greys out together from 10pm, and the only reward is a shared sunrise log.",["Push API","PWA","local-first sync"]),
 ("Grant Graveyard to Garden","Learning",4,"Rejected grant applications get stripped of identifying detail and turned into reusable boilerplate for the next applicant.",["LLM API","Markdown","vector embeddings"]),
 ("Trail Steward","Outdoors",3,"Volunteer crews claim trail segments, log condition reports and earn badges that local parks actually recognize.",["Maps API","Geolocation","QR handoff"]),
 ("One Good Take","Music & Audio",2,"Musicians upload a single 30-second take per day; no editing, no second tries, a public streak of honesty.",["Web Audio API","Service Workers","IndexedDB"]),
 ("Roommate Ledger","Social",1,"Split rent, utilities and revenge — a shared ledger with receipts, reminders and a passive-aggressive emoji layer.",["Stripe","SQLite WASM","Push API"]),
 ("Symptom Weather","Health",4,"Correlate your logged symptoms against local pollen, pressure and air quality to find the triggers you never noticed.",["LLM API","Geolocation","Data Lens" if False else "vector embeddings"]),
 ("Prompt Duel","AI & Copilots",2,"Two people, one image prompt, thirty seconds; the crowd picks the better generation and the loser's prompt goes public.",["LLM API","WebSockets","Canvas 2D"]),
 ("Handoff","Dev Tools",3,"A living document that captures everything a departing engineer knew, prompted by questions their teammates ask too late.",["Markdown","CRDTs","Edge Functions"]),
 ("Second Shelf","Social",2,"A book-lending network where the physical copy carries a QR sticker and every borrower leaves a note inside the record.",["QR handoff","Geolocation","PWA"]),
 ("Micro-Dose of Math","Learning",1,"One proof, one puzzle, one minute, every morning — with a streak that resets brutally and a hint shop.",["Canvas 2D","IndexedDB","Push API"]),
 ("Noise Complaint Choir","Music & Audio",4,"Turns city noise complaints into a generative ambient composition, so the loudest block becomes the lead instrument.",["Web Audio API","WebGL","LLM API"]),
 ("The Long Table","Food & Drink",3,"Strangers sign up for one seat at a communal dinner; the app handles menus, allergies, split bills and the seating graph.",["Stripe","Geolocation","iCal feeds"]),
 ("Patch Tuesday","Dev Tools",2,"A weekly ritual that shows every dependency that broke, who broke it, and the one-line fix the community found first.",["RSS parsing","Edge Functions","Markdown"]),
 ("Fossil Hunter","Learning",4,"Citizen scientists label museum specimen photos in thirty-second bursts; accuracy tiers unlock access to unreleased collections.",["in-browser OCR","virtualized lists","Web Workers"]),
 ("Night Shift Nurse Net","Health",3,"A private feed that only wakes between 10pm and 7am, for the people whose entire social life runs on inverted hours.",["Push API","WebSockets","passkeys"]),
 ("One Room Gallery","Creative",2,"A WebGL gallery where each visitor is a soft light; artworks only become visible when someone stands near them.",["WebGL","Three.js","WebSockets"]),
 ("Recipe Relic","Food & Drink",2,"Upload a handwritten family recipe card, get it transcribed, scaled, and permanently archived with the story behind it.",["in-browser OCR","LLM API","File System Access"]),
 ("Split Screen Study","Learning",2,"Two strangers, one silent video room, a shared pomodoro and a rule: if one leaves, both lose the session credit.",["WebRTC","WebSockets","PWA"]),
 ("Curb Alert","Social",1,"Somebody puts a free couch on the curb; the block finds out in ninety seconds with photos and a claimed-by flag.",["Geolocation","Push API","PWA"]),
 ("Fretboard Oracle","Music & Audio",3,"A guitar trainer that listens through the microphone, maps what you actually played, and drills the two notes you keep missing.",["Web Audio API","Web Workers","Canvas 2D"]),
 ("Deadline Weather","Productivity",2,"A calm forecast of your next two weeks rendered as weather: a storm front of overlapping deadlines you can see coming.",["iCal feeds","Canvas 2D","virtualized lists"]),
]

def build():
    ideas, seen = [], set()
    def add(t,b,c,d,tags,r=None):
        t = t.strip()
        if t in seen: return False
        seen.add(t)
        ideas.append(dict(t=t,b=b.strip(),c=c,d=d,tags=list(dict.fromkeys(tags))[:4],
                          r=r or random.choices(["Common","Uncommon","Rare","Epic","Legendary"],
                                                weights=[46,26,18,8,2])[0],
                          w={1:"weekend",2:"1–2 weeks",3:"2–4 weeks",4:"1–2 months",5:"3+ months"}[d],
                          spark=random.randint(55,99)))
        return True

    for t,c,d,b,tags in FLAGSHIP:
        add(t,b,c,d,tags,"Legendary" if d>=4 else "Epic")

    pairs = [(sp,sm,sc,mn,mk,mv,mw) for sp,sm,sc in S for mn,mk,mv,mw in M]
    random.shuffle(pairs)

    TF = [
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"{mn} for {tc(sp)}",
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"{disp(sm)} {mn}",
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"{disp(sm)} {tc(mk)}",
      lambda sp,sm,sc,mn,mk,mv,mw,who: (f"{cap(iv(mv))} {tc(sp)}" if iv(mv) else f"{mn} for {tc(sp)}"),
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"{mn} × {tc(sp)}",
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"{disp(sm)} {mn} for {tc(who)}",
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"The {disp(sm)} {tc(mk)}",
    ]
    VF = lambda v, o: " ".join(v.replace("{o}", o).split())
    FEAT = ["one live leaderboard","zero notifications","offline-first sync","a single daily prompt",
            "a public archive","a five-minute timer","one shared cursor","a printable export"]
    BF = [
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"A{'' if art(mn)=='a' else 'n'} {mn.lower()} where {who} {VF(mv,sp)}. {mw}",
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"{cap(who)} {VF(mv,sp)} in one shared {mk}. {mw}",
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"Everything about {sp}, in a single {mk}. {cap(who)} {VF(mv,'them')}, compare, and keep coming back. {mw}",
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"{mw} Built for {who} who {VF(mv,sp)}.",
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"Turn {sp} into a{'' if art(mn)=='a' else 'n'} {mn.lower()}. {cap(who)} {VF(mv,'them')} every day — {mw[0].lower()+mw[1:]}",
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"For {who} who {VF(mv,sp)}: {art(mk)} {mk} with {random.choice(FEAT)}. {mw}",
      lambda sp,sm,sc,mn,mk,mv,mw,who: f"{cap(sp)} meet a{'' if art(mn)=='a' else 'n'} {mn.lower()}. {cap(who)} {VF(mv,'them')} together and the {mk} does the rest. {mw}",
    ]

    i = 0
    for sp,sm,sc,mn,mk,mv,mw in pairs:
        if len(ideas) >= 500: break
        pool = AUD.get(sc, [])
        who = random.choice(pool) if (pool and random.random() < .62) else random.choice(GEN_WHO)
        title = TF[i % len(TF)](sp,sm,sc,mn,mk,mv,mw,who)
        title = " ".join(title.split())
        if title in seen or len(title) > 46: 
            i += 1; continue
        blurb = BF[i % len(BF)](sp,sm,sc,mn,mk,mv,mw,who)
        if random.random() < .38: blurb += " " + random.choice(EXTRA)
        d = random.choices([1,2,3,4,5], weights=[14,26,32,20,8])[0]
        cat = "AI & Copilots" if mn in ("AI Copilot","Prompt Engine","Remix Engine") and random.random()<.75 else sc
        mtag = mn
        tags = random.sample(TECH,2) + [mtag, cat.split()[0]]
        if not add(title, blurb, cat, d, tags): 
            i += 1; continue
        i += 1

    random.shuffle(ideas)
    for n,it in enumerate(ideas,1): it["n"] = n
    return ideas

ideas = build()
assert len(ideas) == 500, len(ideas)
assert len({i["t"] for i in ideas}) == 500
for it in ideas: it["id"] = f"C{it['n']:03d}"
with open("ideas.json","w",encoding="utf-8") as f:
    json.dump(ideas,f,ensure_ascii=False,separators=(",",":"))
print("count:",len(ideas))
print("rarity:",Counter(i["r"] for i in ideas))
print("cats:",Counter(i["c"] for i in ideas))
print("avg blurb:",round(sum(len(i["b"]) for i in ideas)/500,1),"max title:",max(len(i["t"]) for i in ideas))
for i in random.sample(ideas,18):
    print(f'[{i["n"]:03d}|{i["r"][:4]}|{i["c"]}] {i["t"]}\n     {i["b"]}')
