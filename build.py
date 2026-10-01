#!/usr/bin/env python3
"""
Pro Gen Plumbing — static site builder.
Run `python3 build.py` from this folder; it (re)writes every .html file.
Edit the CONTENT section below (business info, services, reviews, FAQs) and rebuild.
The generated HTML is plain and can also be edited directly if you prefer.
"""
import os, html, json, re, hashlib

# ============================================================
# CONTENT — edit here
# ============================================================
BIZ = {
    "name": "Pro Gen Plumbing",
    "domain": "https://progenplumbing.com",   # live site address — used for canonical URLs, sitemap, link previews, schema
    "owner": "Matthew",
    "phone_display": "(647) 804-3744",
    "phone_tel": "+16478043744",
    "sms": "sms:+16478043744",
    "email": "progenplumbing@gmail.com",
    "address_line": "2300 St Clair Ave W",
    "city": "Toronto",
    "province": "ON",
    "postal": "M6N 0B3",
    "instagram": "https://www.instagram.com/progenplumbing",
    # Exact Google Business Profile listing (CID link — opens Pro Gen's own listing, not a search)
    "google_maps": "https://www.google.com/maps?cid=4772354518637221355",
    # "Leave a review" link. Swap for the short link from Google Business Profile → "Ask for reviews"
    # (looks like https://g.page/r/XXXX/review) — it opens the review box directly.
    "google_review": "https://www.google.com/maps?cid=4772354518637221355",
    "map_embed": "https://www.google.com/maps?q=Pro+Gen+Plumbing,+2300+St+Clair+Ave+W,+Toronto,+ON+M6N+0B3&z=14&output=embed",
    "geo": (43.6704175, -79.4781342),
    "rating": "5.0",
    "review_count": "37",   # keep in sync with Google (was 16; Google showed 37 on Oct 1 2026)
    "hours_short": "Mon–Sun · By appointment",
    "hours_long": "Open 7 days a week by appointment. Same-day and evening availability — call or text and we'll fit you in.",
    "form_action": "https://formspree.io/f/mbgleejo",   # Formspree form "Website contact form" (ProGen Plumbing project) — emails each request to Matthew
    "tagline": "Where precision meets plumbing.",
    "founded": "2025",
}

AREAS_CORE = ["Toronto", "Etobicoke", "North York", "York", "East York", "Scarborough",
              "Mississauga", "Brampton", "Vaughan", "Woodbridge", "Richmond Hill", "Markham",
              "Oakville", "Burlington", "Milton", "Caledon", "Pickering", "Ajax", "Whitby", "Newmarket", "Aurora"]
AREAS_LOCAL = ["The Junction", "Stockyards", "Corso Italia", "Bloor West Village", "High Park", "Roncesvalles",
               "Davenport", "Weston", "Mount Dennis", "Rockcliffe-Smythe", "Earlscourt", "Dovercourt",
               "Runnymede", "Swansea", "Baby Point", "Humber Summit", "Downsview", "Liberty Village", "Parkdale", "Little Italy"]

SERVICES = [
    {
        "slug": "emergency-plumbing",
        "seo_title": "Emergency Plumber in Toronto & the GTA",   # <title> tag — keep under ~60 characters with " | Pro Gen Plumbing"
        "name": "Emergency & Same-Day Plumbing",
        "short": "Burst pipe, ceiling leak, no water, overflowing toilet — call and we'll get to you the same day, weekends included.",
        "icon": "alert",
        "featured": True,
        "hero_sub": "Leaks don't wait for Monday. Neither do we.",
        "intro": [
            "A plumbing emergency is stressful, messy, and gets more expensive the longer it waits. Pro Gen Plumbing offers same-day response across the GTA — including evenings and weekends — for problems that can't sit until the next business day.",
            "One of our recent customers called on a Sunday morning about water coming through their ceiling. Matthew was there the same day, opened the drywall, found and repaired the leak, and had a drywall installer patch the ceiling — all before dinner. That's the standard we hold ourselves to.",
        ],
        "sections": [
            ("What counts as a plumbing emergency?", "ul", [
                "Burst or frozen pipes",
                "Active leaks from ceilings, walls, or under floors",
                "Overflowing toilets or sewage backing up",
                "No water, or no hot water, in the home",
                "A shut-off valve that won't close",
                "Flooding from a failed appliance hose, water heater, or sump pump",
            ]),
            ("What to do while you wait", "ol", [
                ("Shut off the water.", "Find your main shut-off (usually where the water line enters the house, near the meter) and turn it clockwise. For a single fixture, use the small valve under the sink or behind the toilet."),
                ("Kill the power if water is near electrical.", "If water is dripping near outlets, lights, or the panel, switch off the breaker for that area."),
                ("Contain the water.", "Buckets, towels, and moving furniture out of the way save you a lot of cleanup later."),
                ("Call us.", "Tell us what's happening and send a photo if you can — it helps us show up with the right parts."),
            ]),
            ("How we handle emergencies", "ol", [
                ("Fast callback.", "We answer or call back quickly, ask a few questions, and give you an honest arrival window."),
                ("Stop the damage first.", "Isolate the leak and make the situation safe before anything else."),
                ("Diagnose and quote.", "We find the actual cause, explain it plainly, and give you a price before repairs begin."),
                ("Fix it properly.", "A real repair, not a temporary patch — and we clean up when we're done."),
            ]),
        ],
        "faqs": [
            ("Do you charge extra for same-day or weekend calls?", "We keep pricing fair and transparent. You'll get a clear quote before we start, and we'll tell you upfront if timing affects the price."),
            ("How fast can you get here?", "It depends where you are in the GTA and what's already booked, but we'll give you an honest arrival window when you call — and we show up when we say we will."),
            ("Should I try to fix it myself first?", "Shut off the water and make things safe, but avoid chemical drain cleaners or taking fittings apart — that often makes the repair bigger."),
        ],
    },
    {
        "slug": "leak-detection-repair",
        "seo_title": "Leak Detection & Repair in Toronto",   # <title> tag — keep under ~60 characters with " | Pro Gen Plumbing"
        "name": "Leak Detection & Repair",
        "short": "Ceiling stains, damp walls, a water bill that jumped — we find the source and fix it, not just the symptom.",
        "icon": "drop",
        "featured": True,
        "hero_sub": "Find it fast. Fix it once.",
        "intro": [
            "Hidden leaks quietly damage drywall, flooring, and framing, and feed mold. Pro Gen Plumbing tracks leaks to their source — supply lines, drain lines, shut-off valves, fixture connections, or pipe joints inside walls and ceilings — and repairs them properly.",
            "We explain what we found and why it happened, then give you a clear price before any repair work starts.",
        ],
        "sections": [
            ("Signs you may have a hidden leak", "ul", [
                "Water stains or bubbling paint on ceilings or walls",
                "A musty smell, or mold appearing in one spot",
                "Unexplained increase in your water bill",
                "Low water pressure at one or more fixtures",
                "Warm spots on the floor (hot water line) or a water meter that moves when nothing is running",
                "Dripping sounds inside a wall",
            ]),
            ("Common leaks we repair", "ul", [
                "Leaking or seized shut-off valves under sinks and toilets",
                "Faucet and supply-line leaks",
                "Pipe joint and fitting leaks in ceilings and walls",
                "Drain and P-trap leaks under kitchen and bathroom sinks",
                "Toilet base and tank leaks",
                "Shower and tub drain leaks",
            ]),
            ("Our process", "ol", [
                ("Inspection.", "We trace the water back to its source rather than guessing from where it shows up."),
                ("Minimal opening.", "If we need to open a wall or ceiling, we keep the cut as small as possible."),
                ("Clear quote.", "You get the price and the plan before we start."),
                ("Repair and test.", "We fix the leak, run the system, and confirm it's dry."),
                ("Finish.", "Need the drywall patched? We can arrange a finisher so you're not left with a hole."),
            ]),
        ],
        "faqs": [
            ("Do you fix the drywall afterwards?", "We're plumbers first, but we work with drywall installers and can arrange the patch so the job is finished end to end."),
            ("How do you find a leak inside a wall?", "By reading the evidence — where water shows, which fixtures are nearby, pressure tests, and opening the smallest section possible in the right place."),
            ("Is a slow drip really a big deal?", "Yes. A small drip inside a wall can rot framing and grow mold over months. It's much cheaper to fix early."),
        ],
    },
    {
        "slug": "drain-cleaning",
        "seo_title": "Drain Cleaning & Clogged Drains in Toronto",   # <title> tag — keep under ~60 characters with " | Pro Gen Plumbing"
        "name": "Drain Cleaning & Clogged Drains",
        "short": "Slow sinks, gurgling tubs, backed-up kitchen drains — cleared properly so they stay clear.",
        "icon": "drain",
        "featured": True,
        "hero_sub": "Clear it right — not just for a week.",
        "intro": [
            "Grease, hair, soap scum, and food waste build up inside drain lines until water can't get through. Store-bought chemical cleaners rarely remove the buildup and can damage older pipes. We clear the line mechanically so the problem doesn't come straight back.",
            "Kitchen sinks, bathroom sinks, tubs and showers, toilets, laundry drains — if it's slow or blocked, call us.",
        ],
        "sections": [
            ("Warning signs", "ul", [
                "Water drains slowly in a sink, tub, or shower",
                "Gurgling sounds from drains or the toilet",
                "Bad smells coming from a drain",
                "The same drain clogs again and again",
                "More than one fixture is slow at the same time (often a main line issue)",
            ]),
            ("How we clear a drain", "ol", [
                ("Find the blockage.", "We determine whether it's a local clog at the fixture or something further down the line."),
                ("Clear it mechanically.", "Snaking/augering removes the buildup instead of pushing it further along."),
                ("Check the trap and connections.", "A lot of 'clogs' are actually a bad P-trap or a poorly sloped drain — we fix the cause."),
                ("Test the flow.", "We run water and confirm the drain is clear before we leave."),
            ]),
            ("Why skip the chemical drain cleaner?", "ul", [
                "It often sits on top of the clog rather than removing it",
                "It can corrode older metal pipes and damage seals",
                "It's dangerous if a plumber later has to open the line",
                "A mechanical clean removes the buildup completely",
            ]),
        ],
        "faqs": [
            ("How often should drains be cleaned?", "For most homes, a preventative clean every 1–2 years keeps things flowing. Heavy kitchen use or older plumbing may need it more often."),
            ("Can you fix a drain that keeps clogging?", "Yes — a recurring clog usually means the cause hasn't been dealt with. We look at slope, trap condition, venting, and buildup in the line."),
            ("Do you do main sewer lines?", "We handle the common residential cases and can arrange a camera inspection or specialized crew for major sewer line work — we'll be honest about what's needed."),
        ],
    },
    {
        "slug": "faucet-fixture-installation",
        "seo_title": "Faucet & Fixture Installation in Toronto",   # <title> tag — keep under ~60 characters with " | Pro Gen Plumbing"
        "name": "Faucet, Sink & Fixture Installation",
        "short": "New kitchen faucet, vanity, sink, shower head, or shut-off valves — installed clean and leak-free.",
        "icon": "faucet",
        "featured": True,
        "hero_sub": "Clean installs that work perfectly the first time.",
        "intro": [
            "Fixture installation is one of the things customers mention most in our reviews — kitchen faucets and drains, bathroom vanities, sinks, and shut-off valves, installed professionally, tidy, and leak-free.",
            "Bring your own fixture or ask us to recommend one. Either way, we make sure it's compatible with your existing plumbing before we start.",
        ],
        "sections": [
            ("What we install", "ul", [
                "Kitchen and bathroom faucets",
                "Kitchen sinks, bathroom sinks, and vanities",
                "Sink drains, strainers, and P-traps",
                "Shower heads, tub spouts, and shower valves",
                "Shut-off valves and supply lines",
                "Garbage disposals and dishwasher connections",
                "Laundry tubs and washing machine hookups",
            ]),
            ("Why hire a plumber for a faucet?", "ul", [
                "Old shut-off valves often seize or leak the moment they're touched",
                "Mismatched drain heights and tailpieces are the #1 cause of under-sink leaks",
                "Proper sealing and torque prevents the slow drip that ruins a cabinet",
                "We test everything under pressure before we leave",
            ]),
            ("How it works", "ol", [
                ("Send us a photo.", "A quick picture of the fixture and the under-sink area lets us quote accurately."),
                ("We confirm compatibility.", "Hole spacing, drain size, valve type — we check before we start."),
                ("Install and test.", "Clean install, everything tightened and sealed, leak-tested."),
                ("We clean up.", "You get a working fixture and a clean cabinet, not a pile of packaging."),
            ]),
        ],
        "faqs": [
            ("Can I supply my own faucet or vanity?", "Absolutely. Send us the model or a photo and we'll confirm it'll work with your plumbing before the appointment."),
            ("How long does a faucet install take?", "Usually about an hour, longer if shut-off valves or drain parts also need replacing — we'll tell you upfront."),
            ("Do you replace old shut-off valves at the same time?", "We recommend it if they're old or stiff. It's a small add-on that prevents a much bigger problem later."),
        ],
    },
    {
        "slug": "toilet-repair-installation",
        "seo_title": "Toilet Repair & Installation in Toronto",   # <title> tag — keep under ~60 characters with " | Pro Gen Plumbing"
        "name": "Toilet Repair & Installation",
        "short": "Running, leaking, wobbling, or constantly clogging toilets — repaired or replaced, same visit where possible.",
        "icon": "toilet",
        "featured": True,
        "hero_sub": "Stop the running, the wobbling, and the water bill.",
        "intro": [
            "A running toilet can waste hundreds of litres a day. A wobbling one can be leaking at the base without you noticing. We repair the common failures — fill valves, flappers, flush valves, wax rings, supply lines — and install new toilets when replacement makes more sense.",
        ],
        "sections": [
            ("Common toilet problems we fix", "ul", [
                "Toilet runs constantly or refills on its own",
                "Weak or incomplete flush",
                "Water at the base of the toilet",
                "Toilet rocks or wobbles",
                "Frequent clogging",
                "Leaking supply line or shut-off valve",
            ]),
            ("Repair or replace?", "ul", [
                "Repair: single failed part (flapper, fill valve, wax ring) on a toilet that's otherwise in good shape",
                "Replace: cracked tank or bowl, very old high-water-use models, or repeated repairs",
                "We'll give you both options with honest pricing and let you decide",
            ]),
        ],
        "faqs": [
            ("Can you install a toilet I bought myself?", "Yes. Let us know the model and we'll bring the right wax ring, bolts, and supply line."),
            ("Why does my toilet keep clogging?", "Often a partial blockage in the trap, a low-flow model that isn't flushing fully, or a drain issue further down. We diagnose which one it is."),
        ],
    },
    {
        "slug": "bathroom-kitchen-renovation-plumbing",
        "seo_title": "Bathroom & Kitchen Reno Plumbing in Toronto",   # <title> tag — keep under ~60 characters with " | Pro Gen Plumbing"
        "name": "Bathroom & Kitchen Renovation Plumbing",
        "short": "Full bathroom renos, new vanities, relocated fixtures, kitchen rough-ins — planned around your budget.",
        "icon": "reno",
        "featured": True,
        "hero_sub": "Renovation plumbing planned around your budget — not the other way around.",
        "intro": [
            "Planning a bathroom or kitchen renovation? Matthew will come to your home, look at what's actually there, and walk you through what will and won't work with your budget — instead of guessing over the phone. Customers consistently mention that in-person, no-pressure planning as the reason they chose Pro Gen.",
            "From a straightforward vanity and faucet swap to a full bathroom reno with relocated fixtures, we handle the plumbing and coordinate the other trades you need.",
        ],
        "sections": [
            ("Renovation plumbing services", "ul", [
                "Full bathroom renovations — plumbing scope and coordination",
                "Vanity, sink, and faucet installation",
                "Shower and tub valve installation and relocation",
                "Toilet relocation and installation",
                "Kitchen sink, faucet, dishwasher, and fridge line hookups",
                "Rough-in plumbing for new layouts",
                "Coordination with tile, drywall, and finishing trades",
            ]),
            ("How a renovation works with us", "ol", [
                ("In-home consultation.", "We look at the space, the existing plumbing, and your goals, and give you realistic options."),
                ("Clear scope and quote.", "You know what's included, what's optional, and what it costs before anything starts."),
                ("Rough-in.", "New lines, valves, and drains are installed and tested before walls close."),
                ("Finish.", "Fixtures installed once tile and finishes are done — set, sealed, and tested."),
                ("Clean handover.", "We clean up after ourselves. Customers mention it, so we keep doing it."),
            ]),
        ],
        "faqs": [
            ("Can you manage the whole renovation or just plumbing?", "Plumbing is our trade. For everything else — tile, drywall, electrical — we can bring in people we trust and coordinate, or work alongside your contractor."),
            ("Do I need permits?", "It depends on the scope. Moving fixtures or adding drains usually does; a straight swap usually doesn't. We'll tell you what applies."),
            ("How do you keep the project on budget?", "By being honest at the consultation about what's worth doing and what isn't, and quoting the full scope before we begin."),
        ],
    },
]

REELS = [
    ("https://www.instagram.com/reel/DaRkr-1My1V/", "Project reel 1"),
    ("https://www.instagram.com/reel/DUKQE5vjZ0p/", "Project reel 2"),
]
# ---- Job photos -------------------------------------------------------------
# Every photo on the site lives here. To add one: drop a JPG in assets/ (about 1050×1400, under ~200 KB),
# add a line below, then use its key in WORK_PHOTOS / HOME_WORK_PHOTOS / SERVICE_PHOTO.
# "focus" = which part of the photo stays visible when a box crops it (horizontal% vertical%).
PHOTOS = {
    "ensuite":    {"file": "job-luxury-ensuite.jpg", "focus": "50% 30%",
                   "alt": "Luxury ensuite with a smoked-glass freestanding tub, crystal chandelier and a curbless walk-in shower with brushed-gold fixtures",
                   "caption": "Luxury ensuite — curbless walk-in shower, linear drain and freestanding tub"},
    "onyx":       {"file": "job-onyx-slab-shower.jpg", "focus": "50% 45%",
                   "alt": "Bookmatched onyx-look slab shower with brushed-gold hand shower, body jets, towel bar and linear drain behind frameless glass",
                   "caption": "Slab shower — hand shower, body jets and linear drain"},
    "green":      {"file": "job-green-tile-shower.jpg", "focus": "50% 45%",
                   "alt": "Walk-in shower with green vertical tile, brushed-gold rain head, hand shower and thermostatic valve behind a frameless glass door",
                   "caption": "Walk-in shower — rain head, hand shower and thermostatic valve"},
    "tub":        {"file": "job-ensuite-freestanding-tub.jpg", "focus": "50% 55%",
                   "alt": "Bright ensuite with a fluted freestanding tub, floor-mounted gold tub filler and a double vanity with gold faucets",
                   "caption": "Ensuite — freestanding tub filler and double vanity"},
    "curbless":   {"file": "job-curbless-shower.jpg", "focus": "50% 70%",
                   "alt": "Curbless walk-in shower with frameless glass, gold rain head and hand shower, next to a wall-hung toilet",
                   "caption": "Curbless shower and wall-hung toilet"},
    "inprogress": {"file": "job-shower-tiling-in-progress.jpg", "focus": "50% 85%",
                   "alt": "Large-format porcelain shower mid-renovation: floor sloped to a centre drain, recessed niche and valve rough-ins ready for fixtures",
                   "caption": "Shower mid-build — floor sloped to the drain, valves roughed in"},
}
HERO_PHOTO = ("job-hero-ensuite.jpg", PHOTOS["ensuite"]["alt"])   # landscape crop of the ensuite photo

# Our Work page gallery (all photos, best first)
WORK_PHOTOS = ["ensuite", "onyx", "green", "tub", "curbless", "inprogress"]
# "Recent work" strip on the home page (shown next to the Instagram reels) — photos not already used higher up the page
HOME_WORK_PHOTOS = ["curbless", "inprogress"]

# One photo per service page
SERVICE_PHOTO = {
    "emergency-plumbing": "ensuite",
    "leak-detection-repair": "onyx",
    "drain-cleaning": "inprogress",
    "faucet-fixture-installation": "green",
    "toilet-repair-installation": "curbless",
    "bathroom-kitchen-renovation-plumbing": "tub",
}

OTHER_SERVICES = ["Water heater repair & replacement", "Shut-off valve replacement", "Sump pump service",
                  "Garbage disposal installation", "Dishwasher & fridge water lines", "Laundry hookups",
                  "Outdoor hose bibs", "Pipe repair & repiping", "Water pressure problems"]

# Real Google reviews (public). Names shortened to first name + initial for the website.
REVIEWS = [
    ("Nicolas T.", "NT", "I called Matthew on a Sunday morning for a leak I had coming from my ceiling. He came same day, cut open the drywall, located the leak, repaired it and got one of his drywall installers to come to repair the ceiling — all in the same day. Price was fair and he was very knowledgeable and transparent. I highly recommend.", "Ceiling leak — same-day repair"),
    ("Domenic L.", "DL", "Matthew was very polite and professional along with his crew. Very responsive, completed a full bathroom reno and even took the time to clean up after his work!", "Full bathroom renovation"),
    ("Anthony S.", "AS", "I've used Pro Gen Plumbing twice now, and both experiences were great. The first time was for a leaking shut-off valve, and the second was to replace a kitchen faucet. They showed up when they said they would and explained everything before starting.", "Shut-off valve & kitchen faucet"),
    ("Zuzana H.", "ZH", "Matthew and his colleague came to our house for a kitchen drain/pipe issue. Matthew was very professional and knowledgeable. He explained what the issue could be and went right to work. He solved everything very quickly.", "Kitchen drain repair"),
    ("Stefano G.", "SG", "I asked about renovating my upstairs bathroom and instead of talking about the details on the phone, he actually came to my house and gave me a few options on what would and wouldn't work with my budget.", "Bathroom renovation consult"),
    ("Gabriel C.", "GC", "Matthew did an excellent job installing my kitchen sink faucet and drain. He was professional, efficient, and the work was clean and high quality. Everything works perfectly.", "Kitchen faucet & drain install"),
    ("Julian S.", "JS", "These guys were great from start to finish. Communication was excellent, and they kept me updated every step of the way. They showed up on time, did quality work, and made the whole process easy.", "Plumbing repair"),
    ("Daniel S.", "DS", "My bathroom faucets needed fixing so I went with the cheapest guy I could find. Big mistake — the work was sloppy. A friend told me to call Pro Gen, and they fixed the fix properly.", "Bathroom faucet repair"),
    ("Elizabeth M.", "EM", "I was home alone and didn't have anyone to help me with my faucet, so Pro Gen came right away, gave me a very fair price and helped me out right away. Thank you again.", "Faucet repair"),
    ("Romeo S.", "RS", "Great plumber and an even better guy to deal with. He's reliable, professional, does clean work, and takes the time to make sure everything is done properly. Definitely someone you can count on.", "General plumbing"),
    ("Christian B.", "CB", "Fantastic! The work that was done was exactly what I wanted. 10/10 service, highly recommend!", "Fixture installation"),
    ("J.", "J", "These guys did some awesome vanity work — very professional, very clean work. 10/10 would recommend.", "Vanity installation"),
]

HOME_FAQS = [
    ("Will I get a price before you start?", "Always. We diagnose the problem, explain what's going on in plain language, and give you a clear price before any work begins. No surprises on the invoice."),
    ("Do you offer same-day service?", "Yes, whenever we can. We work 7 days a week by appointment and have same-day and evening availability across the GTA — a Sunday-morning ceiling leak is something we've handled the same day."),
    ("What areas do you serve?", "All of the Greater Toronto Area. We're based at St. Clair West in Toronto and regularly work across the city, Etobicoke, North York, Scarborough, Mississauga, Vaughan, Brampton, and beyond."),
    ("Can I supply my own faucet, vanity, or toilet?", "Of course. Send us a photo or the model number and we'll confirm it'll work with your plumbing before we come out."),
    ("Can you do a job you don't normally handle?", "If it's plumbing, we'll usually handle it. If a job needs a specialist or a different trade, we'll tell you honestly and bring in someone we trust rather than leave you stuck."),
    ("Do you clean up after the job?", "Yes — it's something customers mention in almost every review. We leave your space the way we found it, minus the plumbing problem."),
]

# ============================================================
# ICONS (inline SVG, Lucide-style, stroke = currentColor)
# ============================================================
def svg(paths, vb="0 0 24 24", fill="none", sw="2"):
    return f'<svg viewBox="{vb}" fill="{fill}" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>'

ICON = {
    "arrow":  svg('<circle cx="12" cy="12" r="10"/><path d="M8 12h8M12 8l4 4-4 4"/>'),
    "phone":  svg('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.9 2z"/>'),
    "chat":   svg('<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'),
    "mail":   svg('<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 7L2 7"/>'),
    "pin":    svg('<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>'),
    "clock":  svg('<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>'),
    "check":  svg('<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>'),
    "star":   svg('<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>', fill="currentColor", sw="0"),
    "chev":   svg('<path d="m6 9 6 6 6-6"/>'),
    "camera": svg('<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z"/><circle cx="12" cy="13" r="3"/>'),
    "wrench": svg('<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'),
    "shield": svg('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>'),
    "broom":  svg('<path d="m13 11 9-9M14.6 12.6c1.7 1.7 1.7 4.4 0 6.1L11 22l-9-9 3.3-3.6c1.7-1.7 4.4-1.7 6.1 0z"/><path d="m5 15 4 4"/>'),
    "tag":    svg('<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L2 12V2h10l8.6 8.6a2 2 0 0 1 0 2.8z"/><circle cx="7" cy="7" r="1.5"/>'),
    "instagram": svg('<rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>'),
    "google": '<svg class="g-badge__logo" viewBox="0 0 48 48" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.6l6.8-6.8C35.8 2.4 30.3 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.9 6.1C12.4 13.6 17.7 9.5 24 9.5z"/><path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.6 3-2.3 5.5-4.8 7.2l7.7 6c4.5-4.2 6.9-10.3 6.9-17.7z"/><path fill="#FBBC05" d="M10.5 28.7c-.5-1.5-.8-3-.8-4.7s.3-3.2.8-4.7l-7.9-6.1C1 16.5 0 20.1 0 24s1 7.5 2.6 10.8l7.9-6.1z"/><path fill="#34A853" d="M24 48c6.3 0 11.7-2.1 15.6-5.7l-7.7-6c-2.1 1.4-4.8 2.3-7.9 2.3-6.3 0-11.6-4.1-13.5-9.9l-7.9 6.1C6.5 42.6 14.6 48 24 48z"/></svg>',
    # service icons
    "alert":  svg('<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>'),
    "drop":   svg('<path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5S12.5 6 12 2c-.5 4-2 6-4 7.5S5 13 5 15a7 7 0 0 0 7 7z"/>'),
    "drain":  svg('<path d="M4 4h6v5a4 4 0 0 0 4 4h6"/><path d="M20 13v7M10 4h2"/><path d="m17 17 3 3 3-3"/>'),
    "faucet": svg('<path d="M12 3v4M8 5h8"/><path d="M12 7a6 6 0 0 1 6 6v1H6v-1a6 6 0 0 1 6-6z"/><path d="M4 14h16"/><path d="M6 14v2a2 2 0 0 0 2 2h1"/><path d="M15 18a1.5 1.5 0 1 0 3 0c0-1-1.5-3-1.5-3s-1.5 2-1.5 3z"/>'),
    "toilet": svg('<path d="M7 3h9a1 1 0 0 1 1 1v8H7z"/><path d="M4 12h16a6 6 0 0 1-6 6h-1l1 3H9l1-3H9a5 5 0 0 1-5-5z"/>'),
    "reno":   svg('<path d="M3 21h18"/><path d="M5 21V8l7-5 7 5v13"/><path d="M9 21v-6h6v6"/>'),
}

# ============================================================
# HELPERS
# ============================================================
def e(s): return html.escape(s, quote=True)

def photo(label, sub="", cls=""):
    return f'''<div class="photo {cls}" role="img" aria-label="{e(label)}">
  <div class="photo__label">{ICON["camera"]}<strong>{e(label)}</strong>{e(sub)}</div>
</div>'''

def img(file, alt, cls="", root="", eager=False, focus=None, size=(1050, 1400)):
    # eager=True for the one image that's visible on first load (helps page speed / LCP)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    style = f' style="object-position: {focus}"' if focus and focus != "50% 50%" else ""
    w, h = size
    return f'<div class="photo photo--img {cls}"><img src="{root}assets/{file}" alt="{e(alt)}" width="{w}" height="{h}"{style} {load}></div>'

def pimg(key, cls="", root="", eager=False):
    """Job photo by its PHOTOS key."""
    p = PHOTOS[key]
    return img(p["file"], p["alt"], cls, root, eager, p.get("focus"))

def reel(url, label):
    return f'''<div class="reel">
  <blockquote class="instagram-media" data-instgrm-permalink="{url}" data-instgrm-version="14">
    <a class="reel__fallback" href="{url}" target="_blank" rel="noopener">
      <span class="reel__play">{ICON["instagram"]}</span>
      <strong>Watch on Instagram</strong>
      <span>{e(label)} · @progenplumbing</span>
    </a>
  </blockquote>
</div>'''

# Instagram's embed.js is heavy, so js/main.js loads it only when a reel scrolls into view.
INSTAGRAM_SCRIPT = ''

def work_figure(key, root=""):
    p = PHOTOS[key]
    return f'''<figure class="work reveal">{pimg(key, "photo--tall", root)}<figcaption>{e(p["caption"])}</figcaption></figure>'''

def work_section(root="", heading="Recent work", show_all_link=True):
    """Home page strip: a couple of photos + the Instagram reels, 4 across."""
    photos = "".join(work_figure(k, root) for k in HOME_WORK_PHOTOS)
    reels = "".join(reel(u, l) for u, l in REELS)
    link = f'<div class="center mt-3">{btn("See all our work", root + "work.html", "btn btn--outline-dark")}</div>' if show_all_link else ""
    return f'''<section class="section" id="work">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">Our Work</span>
      <h2>{e(heading)}</h2>
      <p>Real jobs, not stock photos. Follow <a href="{BIZ["instagram"]}" target="_blank" rel="noopener"><strong>@progenplumbing</strong></a> for project videos and before-and-afters.</p>
    </div>
    <div class="work-grid work-grid--strip">
      {photos}
      {reels}
    </div>
    {link}
  </div>
</section>
{INSTAGRAM_SCRIPT}'''

def ext(href):
    # external links open in a new tab so visitors don't lose the site
    return ' target="_blank" rel="noopener"' if href.startswith("http") else ""

def btn(text, href, cls="btn", icon="arrow"):
    return f'<a class="{cls}" href="{href}"{ext(href)}>{e(text)}{ICON[icon] if icon else ""}</a>'

def call_btn(cls="btn btn--outline", text=None):
    return f'<a class="{cls}" href="tel:{BIZ["phone_tel"]}">{ICON["phone"]}{e(text or "Call " + BIZ["phone_display"])}</a>'

def stars(n=5):
    return '<span class="stars" role="img" aria-label="5 out of 5 stars">' + ICON["star"] * n + '</span>'

def checklist(items, cls=""):
    return f'<ul class="checklist {cls}">' + "".join(f'<li>{ICON["check"]}<span>{e(i)}</span></li>' for i in items) + '</ul>'

def faq_block(faqs, first_open=True):
    out = ['<div class="faq">']
    for i, (q, a) in enumerate(faqs):
        op = " is-open" if (first_open and i == 0) else ""
        exp = "true" if (first_open and i == 0) else "false"
        out.append(f'''<div class="faq__item{op}">
  <button class="faq__q" type="button" aria-expanded="{exp}"><span>{e(q)}</span>{ICON["chev"]}</button>
  <div class="faq__a"><div><p>{e(a)}</p></div></div>
</div>''')
    out.append('</div>')
    return "\n".join(out)

def service_card(s, root=""):
    return f'''<article class="service-card reveal">
  <h3>{e(s["name"])}</h3>
  <p>{e(s["short"])}</p>
  <a class="btn btn--ghost" href="{root}services/{s["slug"]}.html">View details {ICON["arrow"]}</a>
  <div class="service-card__icon">{ICON[s["icon"]]}</div>
</article>'''

def contact_form(root="", compact=False):
    svc_opts = "".join(f'<option>{e(s["name"])}</option>' for s in SERVICES) + '<option>Something else</option>'
    return f'''<form class="form" action="{BIZ["form_action"]}" method="POST" data-validate data-email="{BIZ["email"]}">
  <div class="form__row">
    <label>Name <input type="text" name="name" required autocomplete="name" placeholder="Your name"></label>
    <label>Phone <input type="tel" name="phone" required autocomplete="tel" placeholder="(647) 000-0000"></label>
  </div>
  <div class="form__row">
    <label>Email <input type="email" name="email" autocomplete="email" placeholder="you@example.com"></label>
    <label>Service needed <select name="service">{svc_opts}</select></label>
  </div>
  <label>What's going on? <textarea name="message" required placeholder="Describe the problem — where it is, when it started, and whether it's urgent."></textarea></label>
  <label>Preferred time <input type="text" name="preferred_time" placeholder="e.g. Today after 5pm, or Saturday morning"></label>
  <input type="hidden" name="_subject" value="New request from the Pro Gen Plumbing website">
  <input type="text" name="_gotcha" class="form__hp" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div class="btn-row">
    <button class="btn" type="submit">Request a call back {ICON["arrow"]}</button>
    <span class="form__note">Or call/text <a href="tel:{BIZ["phone_tel"]}">{BIZ["phone_display"]}</a> for the fastest response.</span>
  </div>
  <p class="form__status" role="status" aria-live="polite" hidden></p>
</form>'''

def url(path=""):
    """Absolute URL on the live domain, e.g. url('about.html')."""
    return BIZ["domain"].rstrip("/") + "/" + ("" if path in ("", "index.html") else path)

BIZ_ID = url() + "#business"

def ld(data):
    return '<script type="application/ld+json">' + json.dumps(data, indent=1, ensure_ascii=False) + '</script>'

def schema_ld():
    # Note: no aggregateRating here on purpose — Google doesn't allow a business to mark up its own
    # reviews (it can trigger a structured-data penalty). The stars still show from the Google profile.
    # Opening hours are left out too: Google takes them from the Business Profile.
    lat, lng = BIZ["geo"]
    data = {
        "@context": "https://schema.org",
        "@type": "Plumber",
        "@id": BIZ_ID,
        "name": BIZ["name"],
        "url": url(),
        "telephone": BIZ["phone_tel"],
        "email": BIZ["email"],
        "image": url("assets/og-image.jpg"),
        "logo": url("assets/logo-512.png"),
        "slogan": BIZ["tagline"],
        "address": {"@type": "PostalAddress", "streetAddress": BIZ["address_line"], "addressLocality": BIZ["city"],
                    "addressRegion": BIZ["province"], "postalCode": BIZ["postal"], "addressCountry": "CA"},
        "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
        "hasMap": BIZ["google_maps"],
        "areaServed": [{"@type": "City", "name": a} for a in AREAS_CORE],
        "sameAs": [BIZ["instagram"], BIZ["google_maps"]],
        "priceRange": "$$",
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Plumbing services",
                            "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": url(f"services/{s['slug']}.html")}} for s in SERVICES]},
    }
    site = {"@context": "https://schema.org", "@type": "WebSite", "name": BIZ["name"], "url": url(), "publisher": {"@id": BIZ_ID}}
    return ld(data) + "\n" + ld(site)

def breadcrumb_ld(trail):
    """trail = [(name, path-or-None for current page)], path relative to site root."""
    items = []
    for i, (name, path) in enumerate(trail):
        items.append({"@type": "ListItem", "position": i + 1, "name": name, "item": url(path)})
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})

def service_ld(s):
    return ld({"@context": "https://schema.org", "@type": "Service", "name": s["name"], "serviceType": s["name"],
               "description": s["short"], "url": url(f"services/{s['slug']}.html"),
               "provider": {"@type": "Plumber", "@id": BIZ_ID, "name": BIZ["name"], "telephone": BIZ["phone_tel"]},
               "areaServed": {"@type": "AdministrativeArea", "name": "Greater Toronto Area"}})

def css_js_version():
    # cache-busting: the ?v= changes whenever style.css or main.js changes, so browsers never use a stale copy
    h = hashlib.md5()
    for f in ("css/style.css", "js/main.js"):
        with open(f, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:8]

# ============================================================
# LAYOUT
# ============================================================
LOGO_SRC = 'assets/logo-56.png'
LOGO_SRCSET = 'assets/logo-56.png 1x, assets/logo-112.png 2x, assets/logo-168.png 3x'

def logo_img(root, size=56):
    srcset = ", ".join(f"{root}{part}" for part in LOGO_SRCSET.split(", "))
    return f'<img src="{root}{LOGO_SRC}" srcset="{srcset}" width="{size}" height="{size}" alt="">'

def layout(title, desc, body, current="", root="", extra_head="", path="", noindex=False):
    """path = this page's location relative to the site root (e.g. 'services/drain-cleaning.html') — used for the canonical URL."""
    def nav_link(text, href, key):
        cur = ' aria-current="page"' if current == key else ""
        return f'<a href="{root}{href}"{cur}>{text}</a>'
    sub = "".join(f'<li><a href="{root}services/{s["slug"]}.html">{e(s["name"])}</a></li>' for s in SERVICES)
    v = css_js_version()
    canonical = url(path)
    seo_head = ('<meta name="robots" content="noindex">' if noindex else f'''<link rel="canonical" href="{canonical}">
<meta property="og:url" content="{canonical}">''')
    return f'''<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{seo_head}
<meta name="theme-color" content="#070A0E">
<link rel="icon" href="{root}favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="96x96" href="{root}assets/favicon-96.png">
<link rel="apple-touch-icon" href="{root}assets/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(BIZ["name"])}">
<meta property="og:locale" content="en_CA">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{url("assets/og-image.jpg")}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(BIZ["name"])} — Toronto &amp; GTA plumber">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/style.css?v={v}">
{extra_head}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container">
    <a class="brand" href="{root}index.html" aria-label="{e(BIZ["name"])} home">
      {logo_img(root)}
      <span>Pro Gen Plumbing<small>Toronto &amp; GTA</small></span>
    </a>
    <div class="nav-wrap">
      <ul class="nav">
        <li>{nav_link("Home", "index.html", "home")}</li>
        <li class="has-sub">{nav_link("Services", "services.html", "services")}
          <ul class="sub">{sub}<li><a href="{root}services.html">All services →</a></li></ul>
        </li>
        <li>{nav_link("Our Work", "work.html", "work")}</li>
        <li>{nav_link("Service Areas", "service-areas.html", "areas")}</li>
        <li>{nav_link("About", "about.html", "about")}</li>
        <li>{nav_link("Contact", "contact.html", "contact")}</li>
      </ul>
      <div class="nav-mobile-cta hide-desktop">
        {call_btn("btn")}
        {btn("Request a call back", root + "contact.html", "btn btn--light")}
      </div>
    </div>
    <div class="header-cta">
      <a class="header-phone" href="tel:{BIZ["phone_tel"]}">{ICON["phone"]}<span>{BIZ["phone_display"]}</span></a>
      {btn("Request Service", root + "contact.html", "btn btn--sm")}
      <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false"><span></span></button>
    </div>
  </div>
</header>

<main id="main">
{body}
</main>

<footer class="site-footer">
  <div class="container grid">
    <div>
      <a class="brand" href="{root}index.html">{logo_img(root)}<span>Pro Gen Plumbing<small>Toronto &amp; GTA</small></span></a>
      <p class="mt-2">Professional plumbing for homes across the Greater Toronto Area — repairs, installations, drains, leaks, and renovation plumbing. Fair pricing, clean work, and same-day availability.</p>
      <div class="social">
        <a href="{BIZ["instagram"]}" target="_blank" rel="noopener" aria-label="Instagram">{ICON["instagram"]}</a>
        <a href="{BIZ["google_maps"]}" target="_blank" rel="noopener" aria-label="Google Business Profile">{ICON["pin"]}</a>
      </div>
    </div>
    <div>
      <h2 class="footer__title">Services</h2>
      <ul>{"".join(f'<li><a href="{root}services/{s["slug"]}.html">{e(s["name"])}</a></li>' for s in SERVICES)}</ul>
    </div>
    <div>
      <h2 class="footer__title">Company</h2>
      <ul>
        <li><a href="{root}about.html">About Matthew</a></li>
        <li><a href="{root}work.html">Our work</a></li>
        <li><a href="{root}service-areas.html">Service areas</a></li>
        <li><a href="{root}services.html">All services</a></li>
        <li><a href="{root}contact.html">Contact</a></li>
        <li><a href="{BIZ["google_review"]}" target="_blank" rel="noopener">Leave a Google review</a></li>
      </ul>
    </div>
    <div>
      <h2 class="footer__title">Contact</h2>
      <ul class="contact-list">
        <li>{ICON["phone"]}<a href="tel:{BIZ["phone_tel"]}">{BIZ["phone_display"]}</a></li>
        <li>{ICON["mail"]}<a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a></li>
        <li>{ICON["pin"]}<span>{BIZ["address_line"]}<br>{BIZ["city"]}, {BIZ["province"]} {BIZ["postal"]}</span></li>
        <li>{ICON["clock"]}<span>{BIZ["hours_short"]}<br>Same-day &amp; evening availability</span></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="container">
      <span>© <span id="year">2026</span> {e(BIZ["name"])}. All rights reserved.</span>
      <span>Serving Toronto &amp; the GTA · <a href="{root}contact.html">Get in touch</a></span>
    </div>
  </div>
</footer>

<div class="call-bar">
  {call_btn("btn", "Call")}
  <a class="btn btn--light" href="{BIZ["sms"]}">{ICON["chat"]}Text</a>
  {btn("Request", root + "contact.html", "btn btn--outline")}
</div>

<script src="{root}js/main.js?v={v}" defer></script>
</body>
</html>'''

def page_hero(title, lede, crumbs):
    c = " / ".join(f'<a href="{h}">{e(t)}</a>' if h else f'<span>{e(t)}</span>' for t, h in crumbs)
    return f'''<section class="page-hero">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb">{c}</nav>
    <h1>{e(title)}</h1>
    <p class="lede">{e(lede)}</p>
  </div>
</section>'''

def cta_strip(root=""):
    return f'''<section class="cta-strip">
  <div class="container">
    <div>
      <h2>Leak, clog, or no water right now?</h2>
      <p>Same-day and evening availability across the GTA. Call or text and we'll tell you honestly how fast we can get there.</p>
    </div>
    <div class="btn-row">
      {call_btn("btn btn--light btn--lg")}
      <a class="btn btn--outline btn--lg" href="{BIZ["sms"]}">{ICON["chat"]}Text us</a>
    </div>
  </div>
</section>'''

def reviews_section(root="", limit=6, alt=True, offset=0):
    cards = ""
    for name, ini, text, job in REVIEWS[offset:offset+limit]:
        cards += f'''<article class="review reveal">
  <div class="review__head"><span class="avatar" aria-hidden="true">{ini}</span><div><strong>{e(name)}</strong><small>{e(job)} · Google review</small></div></div>
  {stars()}
  <p>“{e(text)}”</p>
</article>'''
    return f'''<section class="section {"section--alt" if alt else ""}" id="reviews">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">Google Reviews</span>
      <h2>Rated 5.0 by the people we've worked for</h2>
      <p>Every review below is a real Google review from a GTA homeowner. Read them all, or leave your own.</p>
      <div class="mt-2"><a class="g-badge" href="{BIZ["google_maps"]}" target="_blank" rel="noopener">{ICON["google"]}<div><strong>{BIZ["rating"]} <span class="stars" style="color:#F5A623">{ICON["star"]*5}</span></strong><small>Based on {BIZ["review_count"]} Google reviews</small></div></a></div>
    </div>
    <div class="grid grid-3">{cards}</div>
    <div class="center mt-3">{btn("See all reviews on Google", BIZ["google_maps"], "btn btn--outline-dark")}</div>
  </div>
</section>'''

# ============================================================
# PAGES
# ============================================================
def steps_block(root=""):
    steps = [
        ("Call, text, or send a request", "Tell us what's going on. A photo helps us arrive with the right parts."),
        ("We come out and take a look", "For repairs we diagnose on-site. For renovations, Matthew visits and walks through what will and won't work with your budget."),
        ("You get a clear price first", "No work starts until you've seen the price and said yes."),
        ("We do it properly", "Quality parts, clean work, tested before we leave."),
        ("We clean up", "Your home looks the way it did when we arrived — minus the problem."),
    ]
    steps_html = "".join(f'<li class="step reveal"><span class="step__num">{i+1}</span><h3>{e(t)}</h3><p>{e(d)}</p></li>' for i, (t, d) in enumerate(steps))
    return f'''<section class="section" id="process">
  <div class="container grid grid-2">
    <div>
      <span class="eyebrow">How It Works</span>
      <h2>Simple, stress-free, no surprises</h2>
      <ol class="steps mt-3">{steps_html}</ol>
    </div>
    <div class="photo-stack reveal reveal--right">
      {pimg("onyx", "photo--tall", root)}
      <div class="callout callout--accent">
        <div class="icon-circle icon-circle--white">{ICON["phone"]}</div>
        <p class="callout__title">Call or text anytime</p>
        <a href="tel:{BIZ["phone_tel"]}">{BIZ["phone_display"]}</a>
      </div>
    </div>
  </div>
</section>'''

def reviews_slider(root="", alt=False, count=6):
    slides = ""
    for name, ini, text, job in REVIEWS[:count]:
        slides += f'''<div class="slider__slide"><blockquote class="testimonial">
  {stars()}
  <p>“{e(text)}”</p>
  <div class="testimonial__who"><span class="avatar" aria-hidden="true">{ini}</span><div><strong>{e(name)}</strong>{e(job)} · Google review</div></div>
</blockquote></div>'''
    return f'''<section class="section {"section--alt" if alt else ""}" id="reviews">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">Google Reviews</span>
      <h2>Rated 5.0 by the people we've worked for</h2>
      <div class="mt-2"><a class="g-badge" href="{BIZ["google_maps"]}" target="_blank" rel="noopener">{ICON["google"]}<div><strong>{BIZ["rating"]} <span class="stars" style="color:#F5A623">{ICON["star"]*5}</span></strong><small>Based on {BIZ["review_count"]} Google reviews</small></div></a></div>
    </div>
    <div class="slider slider--arrows mx-auto" style="max-width: 900px;">
      <button class="slider__arrow slider__arrow--prev" type="button" aria-label="Previous review">{ICON["chev"]}</button>
      <div class="slider__track">{slides}</div>
      <button class="slider__arrow slider__arrow--next" type="button" aria-label="Next review">{ICON["chev"]}</button>
      <div class="slider__dots"></div>
    </div>
    <div class="center mt-3">{btn("Read all reviews on Google", BIZ["google_maps"], "btn btn--outline-dark")}</div>
  </div>
</section>'''

def page_home():
    featured = [s for s in SERVICES if s["featured"]]
    cards = "".join(service_card(s) for s in featured)
    areas = "".join(f"<li>{e(a)}</li>" for a in AREAS_CORE[:14])

    body = f'''
<section class="hero">
  <div class="hero__bg" aria-hidden="true"></div>
  <div class="container">
    <div class="hero__grid">
      <div class="reveal reveal--left">
        <h1><span class="hero__kicker">Toronto &amp; GTA Plumber</span> Where precision meets plumbing.</h1>
        <p>Plumbing done right the first time, across Toronto &amp; the GTA — repairs, installs, drains, leaks, and renovations. Fair pricing you see before we start, clean work, and same-day availability.</p>
        <div class="mt-2">{checklist(["Same-day & evening availability", "Clear price before any work starts", "Clean, tidy, respectful of your home", "Serving all of the GTA, 7 days a week"])}</div>
        <div class="btn-row mt-3">
          {call_btn("btn")}
          <a class="btn btn--outline" href="{BIZ["sms"]}">{ICON["chat"]}Text us a photo</a>
          {btn("Request a call back", "contact.html", "btn btn--ghost btn--ghost-light")}
        </div>
      </div>
      <div class="hero__aside reveal reveal--right">
        <div class="rating">
          <div class="rating__num"><span>{BIZ["rating"]}</span>{ICON["star"]}</div>
          <div class="rating__meta"><strong>Google rating</strong>from {BIZ["review_count"]} Google reviews</div>
        </div>
        <div class="avatars" aria-hidden="true">{"".join(f'<span class="avatar">{r[1]}</span>' for r in REVIEWS[:4])}<span class="avatar">+{int(BIZ["review_count"])-4}</span></div>
        {img(HERO_PHOTO[0], HERO_PHOTO[1], "photo--hero", eager=True, size=(1200, 900))}
      </div>
    </div>
  </div>
</section>

<section class="section section--alt" id="services">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">Plumbing Services</span>
      <h2>Leaks, clogs, installs, renos — and everything in between</h2>
      <p>Everyday residential plumbing done properly. If it's a job we don't handle ourselves, we'll say so and bring in someone we trust.</p>
    </div>
    <div class="grid grid-3">{cards}</div>
    <p class="center mt-3">Need something not listed? <a href="services.html"><strong>See all services</strong></a> or <a href="tel:{BIZ["phone_tel"]}"><strong>call {BIZ["phone_display"]}</strong></a> — if it's plumbing, we'll figure it out.</p>
  </div>
</section>

{reviews_slider()}

<section class="section section--alt" id="why">
  <div class="container grid grid-2">
    <div class="photo-duo">
      {pimg("onyx", "photo--capsule reveal reveal--left")}
      {pimg("green", "photo--capsule reveal reveal--left")}
    </div>
    <div class="reveal reveal--right">
      <span class="eyebrow">Why Pro Gen</span>
      <h2>A local plumber who shows up, explains things, and does clean work</h2>
      <p>Pro Gen Plumbing is run by Matthew, a Toronto plumber based at St. Clair West. He started Pro Gen because too many homeowners were getting rushed jobs, vague quotes, and a mess left behind. The things customers mention most in their reviews are the things we care about most.</p>
      <div class="feature-card mt-2">
        <div class="feature-row"><div class="icon-circle">{ICON["tag"]}</div><div><h3 class="h4">Price before work</h3><p>You'll see the price and the plan before we touch anything. No surprise line items.</p></div></div>
        <div class="feature-row"><div class="icon-circle">{ICON["wrench"]}</div><div><h3 class="h4">Fix the cause, not the symptom</h3><p>We'd rather find the real problem than sell you a repeat visit.</p></div></div>
        <div class="feature-row"><div class="icon-circle">{ICON["broom"]}</div><div><h3 class="h4">Clean work, clean site</h3><p>Drop cloths, tidy installs, and we take our mess with us.</p></div></div>
        {checklist(["Same-day & evening availability", "In-person quotes for renovations", "Can't do it? We'll find someone who can", "Serving the entire GTA"], "checklist--light")}
      </div>
      <div class="mt-2">{btn("More about Matthew", "about.html", "btn btn--outline-dark")}</div>
    </div>
  </div>
</section>

{work_section()}

{cta_strip()}

<section class="section" id="faq">
  <div class="container grid grid-2" style="align-items:start">
    <div class="photo-stack reveal reveal--left">
      <div class="callout callout--dark"><h3>Honest, clean, <span class="hl">done-right</span> plumbing.</h3></div>
      {pimg("tub", "photo--tall")}
    </div>
    <div>
      <span class="eyebrow">Helpful Answers</span>
      <h2>Frequently asked questions</h2>
      <div class="mt-2">{faq_block(HOME_FAQS[:4])}</div>
      <p class="mt-2">More questions? <a href="contact.html"><strong>See the full FAQ</strong></a> or <a href="tel:{BIZ["phone_tel"]}"><strong>just call</strong></a>.</p>
    </div>
  </div>
</section>

<section class="section booking" id="book">
  <div class="container">
    <div class="booking__card">
      <div>
        <span class="eyebrow">Book a Visit</span>
        <h2>Tell us what's going on</h2>
        <p>Send a few details and we'll call you back to confirm a time. For anything urgent, calling is always fastest.</p>
        <div class="mt-2">
          <div class="feature-row"><div class="icon-circle icon-circle--soft">{ICON["phone"]}</div><div><h3 class="h5">Call or text</h3><p><a href="tel:{BIZ["phone_tel"]}">{BIZ["phone_display"]}</a></p></div></div>
          <div class="feature-row mt-2"><div class="icon-circle icon-circle--soft">{ICON["clock"]}</div><div><h3 class="h5">Hours</h3><p>{e(BIZ["hours_short"])}<br>Same-day &amp; evening availability</p></div></div>
          <div class="feature-row mt-2"><div class="icon-circle icon-circle--soft">{ICON["pin"]}</div><div><h3 class="h5">Based at</h3><p>{e(BIZ["address_line"])}, {e(BIZ["city"])}<br>Serving all of the GTA</p></div></div>
        </div>
      </div>
      <div>{contact_form()}</div>
    </div>
  </div>
</section>

<section class="section section--dark" id="areas">
  <div class="container grid grid-2">
    <div>
      <span class="eyebrow">Service Areas</span>
      <h2>Serving Toronto and the whole GTA</h2>
      <p>We're based at St. Clair West and travel across the Greater Toronto Area — city and suburbs, 7 days a week.</p>
      <div class="mt-2">{btn("See all service areas", "service-areas.html", "btn btn--light")}</div>
    </div>
    <ul class="areas">{areas}<li>+ more</li></ul>
  </div>
</section>
'''
    return layout(f"{BIZ['name']} | Plumber in Toronto & the GTA — Same-Day Service",
                  "5.0-rated Toronto plumber. Leak repair, drain cleaning, fixture installs and bathroom renos across the GTA. Same-day availability — call (647) 804-3744.",
                  body, current="home", extra_head=schema_ld(), path="index.html")

def page_services():
    cards = "".join(service_card(s) for s in SERVICES)
    others = "".join(f"<li>{e(o)}</li>" for o in OTHER_SERVICES)
    body = page_hero("Plumbing Services", "Everyday residential plumbing across Toronto and the GTA — repairs, installations, drains, leaks, and renovation plumbing. Clear pricing before any work begins.",
                     [("Home", "index.html"), ("Services", None)]) + f'''
<section class="section section--alt">
  <div class="container">
    <h2 class="sr-only">Our plumbing services</h2>
    <div class="grid grid-3">{cards}</div>
  </div>
</section>
<section class="section">
  <div class="container grid grid-2" style="align-items:start">
    <div>
      <span class="eyebrow">Also Available</span>
      <h2>More things we handle</h2>
      <p>If it's residential plumbing, chances are we do it. If a job needs a specialist, we'll tell you honestly and bring in someone we trust — you won't be left stuck.</p>
      <ul class="areas mt-2">{others}<li>Ask us →</li></ul>
    </div>
    <div class="aside-card">
      <h3 class="h4">Not sure what you need?</h3>
      <p>Describe the problem or send a photo. We'll tell you what it likely is, what it takes to fix, and roughly what to expect — before anyone comes out.</p>
      <a class="big" href="tel:{BIZ["phone_tel"]}">{ICON["phone"]}{BIZ["phone_display"]}</a>
      {btn("Request a call back", "contact.html", "btn btn--light")}
    </div>
  </div>
</section>
{cta_strip()}
{reviews_section(limit=3, alt=False)}
'''
    return layout(f"Plumbing Services in Toronto & the GTA | {BIZ['name']}",
                  "Emergency plumbing, leak repair, drain cleaning, fixture installs, toilet repair and renovation plumbing across Toronto & the GTA. Upfront pricing.",
                  body, current="services", path="services.html",
                  extra_head=breadcrumb_ld([("Home", ""), ("Services", "services.html")]))

def page_service(s):
    root = "../"
    sections = ""
    for title, kind, items in s["sections"]:
        if kind == "ul":
            sections += f"<h2>{e(title)}</h2><ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"
        else:
            sections += f"<h2>{e(title)}</h2><ol>" + "".join(f"<li><strong>{e(t)}</strong> {e(d)}</li>" for t, d in items) + "</ol>"
    intro = "".join(f"<p>{e(p)}</p>" for p in s["intro"])
    related = "".join(f'<li><a href="{x["slug"]}.html">{e(x["name"])}</a></li>' for x in SERVICES if x["slug"] != s["slug"])
    body = page_hero(s["name"], s["hero_sub"], [("Home", root + "index.html"), ("Services", root + "services.html"), (s["name"], None)]) + f'''
<section class="section">
  <div class="container article">
    <div class="article__body">
      {intro}
      {pimg(SERVICE_PHOTO[s["slug"]], "photo--landscape mt-3 mb-3", root) if s["slug"] in SERVICE_PHOTO else photo(f"Photo: {s['name']} job", "Replace with a real job photo", "photo--landscape mt-3 mb-3")}
      {sections}
      <h2>Frequently asked questions</h2>
      {faq_block(s["faqs"], first_open=False)}
      <div class="mt-3 btn-row">{btn("Request a call back", root + "contact.html")}{call_btn("btn btn--outline-dark")}</div>
    </div>
    <aside class="aside">
      <div class="aside-card">
        <h3 class="h4">Need this fixed?</h3>
        <p>Same-day and evening availability across the GTA. Call or text for the fastest response.</p>
        <a class="big" href="tel:{BIZ["phone_tel"]}">{ICON["phone"]}{BIZ["phone_display"]}</a>
        {btn("Request a call back", root + "contact.html", "btn btn--light")}
      </div>
      <div class="aside-card aside-card--light">
        <h3 class="h4">Why Pro Gen</h3>
        {checklist(["Price before any work starts", "Fix the cause, not the symptom", "Clean work, clean site", "5.0 Google rating"], "checklist--light checklist--1col")}
      </div>
      <div class="aside-card aside-card--light">
        <h3 class="h4">Other services</h3>
        <ul>{related}<li><a href="{root}services.html">All services</a></li></ul>
      </div>
    </aside>
  </div>
</section>
{cta_strip(root)}
'''
    title = f"{s.get('seo_title') or s['name'] + ' in Toronto'} | {BIZ['name']}"
    desc = s["short"] + " Serving Toronto & the GTA. Call (647) 804-3744."
    if len(desc) > 160:
        desc = s["short"] + " Call (647) 804-3744."
    path = f"services/{s['slug']}.html"
    head = breadcrumb_ld([("Home", ""), ("Services", "services.html"), (s["name"], path)]) + "\n" + service_ld(s)
    return layout(title, desc, body, current="services", root=root, path=path, extra_head=head)

def page_about():
    body = page_hero("About Pro Gen Plumbing", "A Toronto plumber who'd rather do the job properly once than come back twice.",
                     [("Home", "index.html"), ("About", None)]) + f'''
<section class="section">
  <div class="container grid grid-2">
    <div class="reveal reveal--left">
      <span class="eyebrow">Meet Matthew</span>
      <h2>Local, hands-on, and honest about what your home actually needs</h2>
      <p>Pro Gen Plumbing is owned and run by Matthew, a Toronto plumber based at St. Clair West. Pro Gen started the way a lot of good trades businesses do: friends and neighbours kept asking for help, the work kept getting recommended, and the reviews followed.</p>
      <p>Matthew still does the work himself, with a small crew when a job calls for it. That means the person who quotes your job is the person who shows up to do it — and the person whose name is on the reviews.</p>
      <p><em>Owner bio placeholder — swap in Matthew's own words here: where he trained, how long he's been in the trade, and why he started Pro Gen.</em></p>
    </div>
    {pimg("ensuite", "photo--tall reveal reveal--right")}
  </div>
</section>

<section class="section section--alt">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">How We Work</span>
      <h2>What you can count on, every job</h2>
    </div>
    <div class="grid grid-3">
      <div class="feature-row reveal"><div class="icon-circle">{ICON["tag"]}</div><div><h3 class="h4">Upfront, fair pricing</h3><p>We diagnose first, then quote. You approve the price before any work starts. Reviewers use the words "fair" and "transparent" a lot — that's on purpose.</p></div></div>
      <div class="feature-row reveal"><div class="icon-circle">{ICON["clock"]}</div><div><h3 class="h4">We show up</h3><p>On time, when we said we would, with an honest arrival window — including same-day for urgent problems and evenings when that's what works for you.</p></div></div>
      <div class="feature-row reveal"><div class="icon-circle">{ICON["wrench"]}</div><div><h3 class="h4">Root cause, not band-aids</h3><p>A recurring clog or a "mystery" leak usually has one real cause. We find it and fix it rather than selling you the same visit twice.</p></div></div>
      <div class="feature-row reveal"><div class="icon-circle">{ICON["broom"]}</div><div><h3 class="h4">Clean work, clean site</h3><p>Tidy installs, drop cloths, and we take our mess with us. Almost every review mentions it.</p></div></div>
      <div class="feature-row reveal"><div class="icon-circle">{ICON["shield"]}</div><div><h3 class="h4">Honest scope</h3><p>If a job needs a specialist or another trade, we say so and bring in someone we trust — you're never left stuck.</p></div></div>
      <div class="feature-row reveal"><div class="icon-circle">{ICON["pin"]}</div><div><h3 class="h4">All of the GTA</h3><p>Based at St. Clair West and working across Toronto, Etobicoke, North York, Scarborough, Mississauga, Vaughan, Brampton, and beyond.</p></div></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container grid grid-2">
    <div class="photo-duo">
      {pimg("inprogress", "photo--capsule reveal reveal--left")}
      {pimg("curbless", "photo--capsule reveal reveal--left")}
    </div>
    <div class="reveal reveal--right">
      <span class="eyebrow">Our Promise</span>
      <h2>Treat every home like it's ours</h2>
      <div class="mt-2">{checklist(["Clear communication from first call to final test", "A price you approve before work starts", "Quality parts and proper repairs", "Respect for your home, your time, and your budget", "Honest advice — even when the answer is 'you don't need that'"], "checklist--light checklist--1col")}</div>
      <div class="stats stats--row mt-4">
        <div class="stat"><div class="stat__num"><span>{BIZ["rating"]}</span></div><div class="stat__label">Google rating</div></div>
        <div class="stat"><div class="stat__num"><span data-count="{BIZ["review_count"]}">{BIZ["review_count"]}</span></div><div class="stat__label">Google reviews</div></div>
        <div class="stat"><div class="stat__num"><span data-count="7">7</span></div><div class="stat__label">Days a week</div></div>
      </div>
    </div>
  </div>
</section>

{steps_block()}
{reviews_section(limit=6)}
{cta_strip()}
'''
    return layout(f"About {BIZ['name']} | Toronto Plumber", "Meet Matthew, the Toronto plumber behind Pro Gen Plumbing. Fair pricing, clean work, honest advice, and same-day availability across the GTA.", body, current="about",
                  path="about.html", extra_head=breadcrumb_ld([("Home", ""), ("About", "about.html")]))

def page_contact():
    body = page_hero("Contact Us", "Call, text, or send a request — we'll get back to you quickly and tell you honestly how soon we can be there.",
                     [("Home", "index.html"), ("Contact", None)]) + f'''
<section class="section">
  <div class="container grid grid-2" style="align-items:start">
    <div>
      <span class="eyebrow">Get In Touch</span>
      <h2>Fastest way to reach us is to call</h2>
      <div class="contact-grid mt-2">
        <div class="contact-item"><div class="icon-circle icon-circle--soft">{ICON["phone"]}</div><div><h3 class="h5">Call or text</h3><p><a href="tel:{BIZ["phone_tel"]}">{BIZ["phone_display"]}</a><br><a href="{BIZ["sms"]}">Send us a text (photos welcome)</a></p></div></div>
        <div class="contact-item"><div class="icon-circle icon-circle--soft">{ICON["mail"]}</div><div><h3 class="h5">Email</h3><p><a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a></p></div></div>
        <div class="contact-item"><div class="icon-circle icon-circle--soft">{ICON["clock"]}</div><div><h3 class="h5">Hours</h3><p>{e(BIZ["hours_short"])}<br>Same-day &amp; evening availability</p></div></div>
        <div class="contact-item"><div class="icon-circle icon-circle--soft">{ICON["pin"]}</div><div><h3 class="h5">Based at</h3><p>{e(BIZ["address_line"])}<br>{e(BIZ["city"])}, {e(BIZ["province"])} {e(BIZ["postal"])}</p></div></div>
      </div>
      <div class="map mt-2"><iframe title="Map — Pro Gen Plumbing, 2300 St Clair Ave W, Toronto" src="{BIZ["map_embed"]}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
      <p class="mt-2"><a href="{BIZ["instagram"]}" target="_blank" rel="noopener"><strong>Follow @progenplumbing on Instagram</strong></a> for recent jobs and before/afters.</p>
    </div>
    <div class="aside-card aside-card--light" style="padding:36px">
      <h3 style="margin:0">Send us a message</h3>
      <p>We'll call or text you back to confirm a time.</p>
      {contact_form()}
    </div>
  </div>
</section>
<section class="section section--alt">
  <div class="container grid grid-2" style="align-items:start">
    <div>
      <span class="eyebrow">Before You Call</span>
      <h2>A few things that help</h2>
      {checklist(["A photo or short video of the problem", "Where it is in the house (and where the water is coming out)", "When it started and whether it's getting worse", "Whether the water is currently shut off", "Your address and a good callback number"], "checklist--light checklist--1col")}
    </div>
    <div>
      <span class="eyebrow">Quick Answers</span>
      <h2>Common questions</h2>
      {faq_block(HOME_FAQS + [
        ("How quickly will you respond?", "We answer or call back as quickly as we can, usually within the hour during the day. For emergencies, calling is always faster than the form."),
        ("Do you charge to come out and look?", "We'll be upfront about any assessment fee when you call, and you'll always get a full price before repairs start."),
        ("Do you offer a warranty?", "We stand behind our work. Ask us about the warranty on labour and parts for your specific job — we'll put it in writing."),
        ("Can you give a quote over the phone?", "For simple jobs like a faucet swap, often yes with a photo. For anything bigger — especially renovations — Matthew will come and look so the quote is actually accurate."),
      ])}
    </div>
  </div>
</section>
{cta_strip()}
'''
    return layout(f"Contact {BIZ['name']} | (647) 804-3744", "Call or text (647) 804-3744, or send a request. Pro Gen Plumbing serves Toronto and the GTA 7 days a week with same-day availability.", body, current="contact",
                  path="contact.html", extra_head=breadcrumb_ld([("Home", ""), ("Contact", "contact.html")]))

def page_work():
    gallery = "".join(work_figure(k) for k in WORK_PHOTOS)
    reels = "".join(reel(u, l) for u, l in REELS)
    body = page_hero("Our Work", "Real projects across the GTA — bathroom renovations, shower builds, fixture installs. Photos and videos straight from the job site.",
                     [("Home", "index.html"), ("Our Work", None)]) + f'''
<section class="section" id="work">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">Recent Projects</span>
      <h2>Real jobs, not stock photos</h2>
      <p>Every photo here is a Pro Gen job in the GTA — from the rough-in behind the walls to the finished fixtures.</p>
    </div>
    <div class="work-grid work-grid--gallery">
      {gallery}
    </div>
  </div>
</section>
<section class="section section--alt">
  <div class="container grid grid-2">
    <div>
      <span class="eyebrow">On Instagram</span>
      <h2>Follow the projects as they happen</h2>
      <p>We post walkthroughs, before-and-afters, and the details most people never see — like a rough-in done properly before the walls close. Follow <a href="{BIZ["instagram"]}" target="_blank" rel="noopener"><strong>@progenplumbing</strong></a>.</p>
      <div class="btn-row mt-2">{btn("Open Instagram", BIZ["instagram"], "btn")}{btn("Request a call back", "contact.html", "btn btn--outline-dark")}</div>
    </div>
    <div class="work-grid work-grid--reels">{reels}</div>
  </div>
</section>
{cta_strip()}
'''
    return layout(f"Our Work — Toronto Plumbing Projects | {BIZ['name']}", "Photos and videos of real Pro Gen Plumbing projects across Toronto and the GTA — bathroom renovations, drain rough-ins, and fixture installations.", body, current="work",
                  path="work.html", extra_head=breadcrumb_ld([("Home", ""), ("Our Work", "work.html")]))

def page_areas():
    core = "".join(f"<li>{e(a)}</li>" for a in AREAS_CORE)
    local = "".join(f"<li>{e(a)}</li>" for a in AREAS_LOCAL)
    body = page_hero("Service Areas", "Based at St. Clair West in Toronto and serving the entire Greater Toronto Area, 7 days a week.",
                     [("Home", "index.html"), ("Service Areas", None)]) + f'''
<section class="section">
  <div class="container grid grid-2" style="align-items:start">
    <div>
      <span class="eyebrow">Across the GTA</span>
      <h2>Cities &amp; regions we serve</h2>
      <p>We regularly work across the whole GTA. Not sure if you're in range? Call — the answer is almost always yes.</p>
      <ul class="areas mt-2">{core}</ul>
    </div>
    <div>
      <span class="eyebrow">Close to Home</span>
      <h2>Toronto west-end neighbourhoods</h2>
      <p>Our home base is St. Clair Ave W near the Stockyards, so these neighbourhoods often get the fastest response.</p>
      <ul class="areas mt-2">{local}</ul>
    </div>
  </div>
</section>
<section class="section section--alt">
  <div class="container grid grid-2">
    <div class="map" style="aspect-ratio: 16/10"><iframe title="Map — Pro Gen Plumbing service area" src="{BIZ["map_embed"].replace("z=14","z=10")}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
    <div>
      <span class="eyebrow">Why It Matters</span>
      <h2>A plumber who knows GTA homes</h2>
      <p>Toronto's older west-end houses, post-war bungalows in Etobicoke and Scarborough, and newer builds in Vaughan and Mississauga all have their own plumbing quirks — galvanized supply lines, clay drains, tight basements, and renovation layers from previous owners. We've seen them, and we plan the job around them.</p>
      <div class="btn-row mt-2">{call_btn("btn")}{btn("Request a call back", "contact.html", "btn btn--outline-dark")}</div>
    </div>
  </div>
</section>
{cta_strip()}
'''
    return layout(f"Service Areas — Toronto & the GTA | {BIZ['name']}", "Pro Gen Plumbing serves Toronto, Etobicoke, North York, Scarborough, Mississauga, Vaughan, Brampton, Markham, Oakville and the whole GTA, 7 days a week.", body, current="areas",
                  path="service-areas.html", extra_head=breadcrumb_ld([("Home", ""), ("Service Areas", "service-areas.html")]))

def page_404():
    # Served by Vercel for any URL that doesn't exist, at any depth — so every link here is root-absolute ("/...").
    root = "/"
    links = "".join(f'<li><a href="{root}services/{s["slug"]}.html">{e(s["name"])}</a></li>' for s in SERVICES)
    body = f'''<section class="page-hero">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}">Home</a> / <span>Page not found</span></nav>
    <h1>Page not found</h1>
    <p class="lede">That page doesn't exist — it may have moved. If you have a plumbing problem, the fastest way to reach us is still a call or text.</p>
    <div class="btn-row mt-3">{call_btn("btn")}{btn("Go to the homepage", root, "btn btn--outline")}</div>
  </div>
</section>
<section class="section">
  <div class="container grid grid-2" style="align-items:start">
    <div>
      <span class="eyebrow">Popular pages</span>
      <h2>Where to next?</h2>
      <ul class="areas mt-2"><li><a href="{root}services.html">All services</a></li><li><a href="{root}work.html">Our work</a></li><li><a href="{root}service-areas.html">Service areas</a></li><li><a href="{root}about.html">About</a></li><li><a href="{root}contact.html">Contact</a></li></ul>
    </div>
    <div class="aside-card aside-card--light">
      <h3 class="h4">Services</h3>
      <ul>{links}</ul>
    </div>
  </div>
</section>'''
    return layout(f"Page not found | {BIZ['name']}", "This page doesn't exist. Call (647) 804-3744 or visit the Pro Gen Plumbing homepage.",
                  body, root=root, noindex=True)

# Pages that go in the sitemap: (path, priority)
SITEMAP = [("index.html", "1.0"), ("services.html", "0.9"), ("contact.html", "0.9"), ("service-areas.html", "0.8"),
           ("work.html", "0.7"), ("about.html", "0.7")] + [(f"services/{s['slug']}.html", "0.8") for s in SERVICES]

def sitemap_xml():
    import datetime
    today = datetime.date.today().isoformat()
    rows = "".join(f"  <url><loc>{url(p)}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>\n" for p, pr in SITEMAP)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}</urlset>\n'

def robots_txt():
    return f"User-agent: *\nAllow: /\n\nSitemap: {url('sitemap.xml')}\n"

def vercel_json():
    """Vercel hosting config: short URLs people can type (progenplumbing.com/contact), caching, security headers."""
    short = {"/home": "/", "/services": "/services.html", "/about": "/about.html",
             "/contact": "/contact.html", "/work": "/work.html", "/our-work": "/work.html", "/gallery": "/work.html",
             "/service-areas": "/service-areas.html", "/areas": "/service-areas.html"}
    short.update({f"/services/{s['slug']}": f"/services/{s['slug']}.html" for s in SERVICES})
    redirects = [{"source": a, "destination": b, "permanent": True} for a, b in short.items()]
    redirects += [{"source": a, "destination": b, "permanent": False} for a, b in
                  {"/reviews": "/about.html#reviews", "/book": "/contact.html", "/quote": "/contact.html"}.items()]
    conf = {
        "$schema": "https://openapi.vercel.sh/vercel.json",
        "cleanUrls": False,
        "trailingSlash": False,
        "redirects": redirects,
        "headers": [
            {"source": "/(.*)", "headers": [
                {"key": "X-Content-Type-Options", "value": "nosniff"},
                {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                {"key": "X-Frame-Options", "value": "SAMEORIGIN"},
                {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(), payment=()"}]},
            # css/js are versioned with ?v=… in every page, so browsers can cache them for a year
            {"source": "/(css|js)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
            {"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=86400, stale-while-revalidate=604800"}]},
        ],
    }
    return json.dumps(conf, indent=2) + "\n"

# ============================================================
# BUILD
# ============================================================
def write(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    write("index.html", page_home())
    write("services.html", page_services())
    write("about.html", page_about())
    write("contact.html", page_contact())
    write("service-areas.html", page_areas())
    write("work.html", page_work())
    for s in SERVICES:
        write(f"services/{s['slug']}.html", page_service(s))
    write("404.html", page_404())
    write("sitemap.xml", sitemap_xml())
    write("robots.txt", robots_txt())
    write("vercel.json", vercel_json())
    if "YOUR_FORM_ID" in BIZ["form_action"]:
        print("\nNOTE: the contact form isn't connected yet — set BIZ['form_action'] to your Formspree URL.")
        print("      Until then, submitting the form opens the visitor's email app addressed to", BIZ["email"])
