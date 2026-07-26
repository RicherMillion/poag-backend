#!/usr/bin/env python3
"""Generate one-page concept demo websites for Sarasota no-website leads. v2.

Design system: per-vertical themes with real display typography (Google
Fonts with system fallbacks), layered textured heroes with watermark
typography, monogram logotypes, sticky nav, stats bands, menu/service
blocks, wave dividers, and a mobile sticky call bar. Each page is a
single self-contained index.html under demo-sites/<slug>/.
"""
import os, re, html

ROOT = os.path.dirname(os.path.abspath(__file__))

# fonts: (display family css, google families query)
FONTS = {
    "slab":    ("'Archivo Black','Arial Black',sans-serif", "Archivo+Black&family=Archivo:wght@400;600"),
    "serif":   ("'Fraunces',Georgia,serif", "Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,800;1,9..144,600&family=Inter:wght@400;600"),
    "condensed":("'Oswald','Arial Narrow',sans-serif", "Oswald:wght@500;700&family=Inter:wght@400;600"),
    "elegant": ("'Playfair Display',Georgia,serif", "Playfair+Display:ital,wght@0,700;0,900;1,700&family=Inter:wght@400;600"),
    "round":   ("'Sora',Verdana,sans-serif", "Sora:wght@600;800&family=Inter:wght@400;600"),
}

# theme: hero base, hero glow, ink-on-light, light bg, card bg, accent, accent-contrast text, font key
THEMES = {
    "ocean":   dict(h1="#07222f", h2="#0b3a4d", glow="#22d3ee", bg="#f4f9fb", ink="#0c2a38", card="#ffffff", ac="#0e7490", ac2="#22d3ee", font="slab"),
    "fresh":   dict(h1="#0c2a17", h2="#14532d", glow="#a3e635", bg="#f4faf5", ink="#122a1b", card="#ffffff", ac="#16a34a", ac2="#a3e635", font="round"),
    "steel":   dict(h1="#0f172a", h2="#1e293b", glow="#f59e0b", bg="#f5f6f8", ink="#111827", card="#ffffff", ac="#b45309", ac2="#f59e0b", font="slab"),
    "barber":  dict(h1="#0d0d0f", h2="#1f2937", glow="#d4af37", bg="#f7f5f0", ink="#141414", card="#ffffff", ac="#a16207", ac2="#d4af37", font="condensed"),
    "blush":   dict(h1="#3f0d24", h2="#831843", glow="#f9a8d4", bg="#fdf4f8", ink="#3d1226", card="#ffffff", ac="#be185d", ac2="#f472b6", font="elegant"),
    "paws":    dict(h1="#0c2b28", h2="#134e4a", glow="#5eead4", bg="#f2fbf9", ink="#0f3733", card="#ffffff", ac="#0f766e", ac2="#2dd4bf", font="round"),
    "vintage": dict(h1="#2b1204", h2="#451a03", glow="#fbbf24", bg="#faf5ee", ink="#33200f", card="#fffdf8", ac="#92400e", ac2="#d97706", font="elegant"),
    "ink":     dict(h1="#0a0a0a", h2="#262626", glow="#ef4444", bg="#f5f5f4", ink="#171717", card="#ffffff", ac="#b91c1c", ac2="#ef4444", font="condensed"),
    "fiesta":  dict(h1="#3f1108", h2="#7c2d12", glow="#fbbf24", bg="#fff9ef", ink="#3c1a10", card="#fffdf7", ac="#c2410c", ac2="#fbbf24", font="serif"),
}

NOISE = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E"
         "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E"
         "%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")

B = lambda **kw: kw
BUSINESSES = [
    B(name="Dominion Exterminators", theme="steel", word="PEST CONTROL", cat="Pest Control",
      tagline="Family-owned pest control, trusted in Sarasota for decades.",
      about="Dominion Exterminators is a family owned and operated pest control company serving Sarasota. Neighbors on Nextdoor have trusted us for years for thorough, honest work at reasonable prices — many customers have stayed with us for 15 years and counting.",
      services=[("Rodent control","Exclusion, trapping, and follow-up done right"),("Roach extermination","Kitchens and whole-home treatment"),("General pest control","Ants, spiders, and seasonal invaders"),("Prevention plans","Quarterly treatments that keep them gone")],
      badges=["Family owned & operated","Nextdoor Neighborhood Favorite","15+ year repeat customers"],
      stats=[("15+","Years with repeat customers"),("100%","Family owned"),("SRQ","Born & based")],
      phone="(941) 266-6659", addr="2116 Bay St, Sarasota, FL 34237"),
    B(name="Walt's Marine Service", theme="ocean", word="MARINE", cat="Marine & Boat Repair",
      tagline="35+ years keeping Sarasota's boats on the water.",
      about="Walt's Marine Service has served Sarasota boaters for more than 35 years. From routine maintenance to major repairs, bring your boat to a shop with decades of hands-on experience and a reputation earned one hull at a time.",
      services=[("Engine service & repair","Outboard and inboard, diagnosed and fixed"),("Routine maintenance","Fluids, impellers, and seasonal service"),("Electrical & systems","Wiring, pumps, and electronics sorted"),("Haul-out & prep","Seasonal prep and storage-ready service")],
      badges=["35+ years in business","Local & independent","Trusted by Sarasota boaters"],
      stats=[("35+","Years in business"),("1000s","Of boats serviced"),("SRQ","Waterfront local")],
      phone="(941) 955-6785", addr="2073 20th St, Sarasota, FL 34234"),
    B(name="Jamaican American Soul Food", theme="fiesta", word="JERK", cat="Jamaican & Soul Food",
      tagline="Real jerk. Real soul. Right on Dr. MLK Jr. Way.",
      about="Authentic Jamaican and Southern soul food cooked the way it should be — slow, seasoned, and generous. Order for pickup or delivery on DoorDash and Grubhub, or come by the restaurant and eat like family.",
      menu=[("Jerk Chicken","Marinated overnight, fired over real heat"),("Oxtail","Fall-apart tender, braised in rich gravy"),("Curry Goat","Island classic, deep and slow-cooked"),("Soul Food Plates","Southern sides done the old-school way")],
      badges=["Authentic island recipes","On DoorDash & Grubhub","Sarasota local favorite"],
      stats=[("2","Cuisines, one kitchen"),("7","Days of flavor"),("MLK","Jr. Way, Sarasota")],
      phone="(941) 260-5723", addr="2025 Dr Martin Luther King Jr Way, Sarasota, FL 34234"),
    B(name="SRQ Marine Services, LLC", theme="ocean", word="RESTORE", cat="Boat Restoration & Repair",
      tagline="Restoration, repower, and repair — done right in Sarasota.",
      about="SRQ Marine Services handles everything from motor maintenance and repowers to full restorations, plus transportation and delivery. Skilled, honest marine work by people who live on this water.",
      services=[("Motor maintenance","Service schedules that protect your engine"),("Repower","New power, matched and installed properly"),("Full restoration","From tired hull to turning heads"),("Transport & delivery","Your boat, moved safely")],
      badges=["Full-service marine shop","Restoration specialists","Local Sarasota crew"],
      phone="(941) 685-9434", addr="510 Mango Ave, Sarasota, FL 34237"),
    B(name="Messenger's Barber Shop & Beauty Salon", theme="barber", word="EST. 1964", cat="Barber Shop & Beauty Salon",
      tagline="Three generations of cuts. Serving Sarasota since 1964.",
      about="A third-generation family business, Messenger's has been cutting hair in Sarasota since 1964. Classic barbering and full salon services, with a 4.8-star rating from the neighbors we've served for decades.",
      services=[("Men's cuts & fades","Sharp, consistent, every visit"),("Women's styling","Cuts and styling in the salon chair"),("Kids' cuts","Patient hands, happy kids"),("Beard & shave","Trims, lines, and hot-lather shaves")],
      badges=["Since 1964","3rd-generation family business","4.8★ rating"],
      stats=[("1964","Year established"),("3","Generations"),("4.8★","Customer rating")],
      phone="(941) 366-3677", addr="3251 17th St #70, Sarasota, FL 34235"),
    B(name="JB SRQ Handyman Services", theme="steel", word="FIXED", cat="Handyman Services",
      tagline="38 years of fixing it right the first time.",
      about="JB SRQ Handyman Services brings 38 years of experience to every job — repairs, installs, and the punch list you've been putting off. A Nextdoor Neighborhood Favorite, BBB-listed and Sarasota through and through.",
      services=[("Home repairs","Done once, done properly"),("Installs","Fixtures, appliances, and hardware"),("Carpentry & trim","Clean lines, tight joints"),("Punch lists","The whole list, knocked out")],
      badges=["38 years in business","Nextdoor Favorite 2022 & 2023","BBB listed"],
      stats=[("38","Years in business"),("2x","Nextdoor Favorite"),("BBB","Listed & local")],
      phone="(941) 228-7763", addr="2737 Hyde Park St, Sarasota, FL 34239"),
    B(name="Economy Lock & Key", theme="steel", word="SECURE", cat="Locksmith",
      tagline="Sarasota's trusted locksmith since 1987.",
      about="Economy Lock & Key has kept Sarasota homes and businesses secure since 1987. BBB accredited, independent, and local — call for lockouts, rekeys, and hardware.",
      services=[("Lockouts","Back inside without the damage"),("Rekeying","New keys, same hardware"),("Installation & repair","Deadbolts, knobs, and smart locks"),("Commercial","Storefront and office hardware")],
      badges=["Since 1987","BBB accredited","Local & independent"],
      stats=[("1987","Year established"),("BBB","Accredited"),("SRQ","Local & independent")],
      phone="(941) 377-8237", addr="5317 Fruitville Rd, Sarasota, FL 34232"),
    B(name="Rose and Dagger Tattoo Studio", theme="ink", word="SIESTA KEY", cat="Tattoo Studio",
      tagline="The only tattoo studio on Siesta Key.",
      about="Custom tattoos steps from the #1 beach in America. Rose and Dagger is Siesta Key's only tattoo studio — walk-ins and appointments, clean work, island atmosphere.",
      services=[("Custom tattoos","Your idea, drawn and inked right"),("Walk-ins","Beach day to fresh ink"),("Cover-ups","Old regrets, new art"),("Flash & souvenirs","Take home something permanent")],
      badges=["Only studio on Siesta Key","Walk-ins welcome","Active on Instagram"],
      stats=[("#1","Beach in America, next door"),("1","Only studio on the Key"),("∞","Souvenir stories")],
      phone="(941) 893-9917", addr="5111 Ocean Blvd Ste H, Siesta Key, FL 34242"),
    B(name="Baja Boys Grill", theme="fiesta", word="TACOS", cat="Taco Truck",
      tagline="Voted Best Food Truck in SRQ.",
      about="Baja-style tacos and burritos out of the Rosemary District. Voted best food truck in Sarasota — find the truck, grab a taco, thank us later.",
      menu=[("Baja Fish Tacos","Crispy, cool crema, proper Baja style"),("Carne Asada Burrito","Packed, grilled, no filler"),("Street Bowls","Everything good, no tortilla required"),("Catering","The truck comes to your party")],
      badges=["Best Food Truck in SRQ","Rosemary District","Catering available"],
      stats=[("#1","Food truck in SRQ"),("100%","Baja style"),("SRQ","Rosemary District")],
      phone=None, addr="Rosemary District, Sarasota, FL"),
    B(name="SRQ Handyman Services", theme="steel", word="AWARDED", cat="Handyman & Remodeling",
      tagline="SRQ Magazine's Best Fence Installer & Best Bathroom Remodeler, 2025.",
      about="Owner-operated since 2018 by Alexander Herbert, SRQ Handyman Services was voted Best Fence Installer and Best Bathroom Remodeler by SRQ Magazine readers in 2025. Quality work, straight answers.",
      services=[("Bathroom remodeling","Award-winning renovations"),("Fence installation","Voted best in Sarasota"),("Handyman work","Repairs and improvements"),("Projects","From idea to done")],
      badges=["SRQ Magazine winner 2025","Owner-operated","Serving Sarasota since 2018"],
      stats=[("2x","SRQ Magazine awards 2025"),("2018","Serving Sarasota since"),("1","Owner on every job")],
      phone=None, addr="Sarasota, FL"),
    B(name="Derek's Handyman Service", theme="steel", word="HANDY", cat="Handyman Services",
      tagline="Honest, affordable handyman work in Sarasota.",
      about="From small fixes to weekend-project rescues, Derek's Handyman Service gets it done without the runaround. Local, reliable, and easy to reach.",
      services=[("General repairs","Small fixes to big saves"),("Assembly & installs","Furniture, fixtures, and more"),("Odd jobs","The stuff nobody else wants"),("Free estimates","Know the price before we start")],
      badges=["Local & owner-operated","Free estimates","Easy scheduling"],
      phone="(941) 405-2821", addr="Sarasota, FL"),
    B(name="GL Grasslands Lawn Care & Landscaping", theme="fresh", word="VERDE", cat="Lawn Care & Landscaping",
      tagline="Full-service lawn care, English y Español.",
      about="GL Grasslands keeps Sarasota yards sharp year-round — mowing, edging, cleanups, and landscaping from a hardworking bilingual crew.",
      services=[("Mowing & edging","Crisp lines, every cut"),("Landscaping","Beds, plants, and curb appeal"),("Cleanups","Overgrown to owned"),("Mulch & planting","Finished and fresh")],
      badges=["Bilingual crew","Licensed Florida LLC","All of Sarasota"],
      phone=None, addr="Sarasota, FL"),
    B(name="Lighthouse Lawn Care FL", theme="fresh", word="DUTY", cat="Lawn Care",
      tagline="Veteran-owned lawn care you can count on.",
      about="Lighthouse Lawn Care is a veteran-owned Sarasota company delivering dependable mowing and lawn maintenance with military attention to detail.",
      services=[("Weekly mowing","Reliable, scheduled, done"),("Edging & trimming","Details that show"),("Cleanups","Reset your yard"),("Maintenance plans","Set it and forget it")],
      badges=["Veteran-owned","Chamber-listed","Reliable scheduling"],
      stats=[("VET","Owned & operated"),("52","Weeks of reliability"),("SRQ","Chamber listed")],
      phone="(941) 323-6020", addr="Sarasota, FL"),
    B(name="Boss Lady Pressure Cleaning", theme="fresh", word="BOSS", cat="Pressure Washing",
      tagline="Woman-owned. Neighborhood Favorite. Spotless results.",
      about="With 12 years of experience, Boss Lady Pressure Cleaning earned Nextdoor's Neighborhood Favorite award in both 2023 and 2024. Driveways, roofs, pool decks — we make it look new again.",
      services=[("House washing","Years of grime, gone in hours"),("Driveways & walks","Back to bright"),("Roof cleaning","Safe, soft-wash clean"),("Decks & lanais","Pool-party ready")],
      badges=["Woman-owned","Nextdoor Favorite 2023 & 2024","12 years experience"],
      stats=[("12","Years experience"),("2x","Nextdoor Favorite"),("100%","Woman-owned")],
      phone="(239) 898-2283", addr="Sarasota, FL"),
    B(name="Southwest Florida Painting and Handyman Services", theme="steel", word="FRESH COAT", cat="Painting & Handyman",
      tagline="First-responder owned. Precision painting and repairs.",
      about="Owned and operated by a first responder, SWFL Painting and Handyman Services brings discipline and care to interior and exterior painting plus general handyman work across Sarasota County.",
      services=[("Interior painting","Clean edges, cleaner job sites"),("Exterior painting","Florida-proof finishes"),("Drywall & repair","Patched, matched, invisible"),("Handyman work","One call, many fixes")],
      badges=["First-responder owned","Interior & exterior","Sarasota County wide"],
      phone=None, addr="Sarasota County, FL"),
    B(name="OCD Cleaning of Sarasota", theme="fresh", word="SPOTLESS", cat="Cleaning Services",
      tagline="Obsessively clean homes and offices.",
      about="OCD Cleaning of Sarasota has been making homes and offices spotless since 2020. Detail-obsessed, dependable, and local.",
      services=[("Home cleaning","Every room, every time"),("Office cleaning","Professional spaces, kept that way"),("Deep cleans","The reset button"),("Recurring service","Clean on a schedule")],
      badges=["Homes & offices","Detail-obsessed","Active Florida LLC"],
      phone="(941) 301-7937", addr="200 Honore Ave, Sarasota, FL 34232"),
    B(name="Sarasota Pooligans", theme="ocean", word="POOL DAY", cat="Pool Service",
      tagline="Weekly pool cleaning without the hassle.",
      about="Sarasota Pooligans is a locally owned pool service offering weekly cleaning, free quotes, and honest work — Monday through Saturday, 7 to 7.",
      services=[("Weekly cleaning","Skim, brush, vacuum, done"),("Chemical balancing","Safe, clear, swimmable"),("Filter care","Equipment that lasts"),("Free quotes","Know before you commit")],
      badges=["Locally owned","Mon–Sat 7am–7pm","Free quotes"],
      hours="Mon–Sat, 7am–7pm",
      phone="(941) 298-4042", addr="Sarasota, FL 34231"),
    B(name="Sarasota Pool Cleaning And Repair", theme="ocean", word="CLEAR", cat="Pool Cleaning & Repair",
      tagline="Cleaning and repairs for Sarasota pools.",
      about="Pool cleaning and repair for Sarasota homeowners — maintenance visits, equipment fixes, and green-to-clean rescues.",
      services=[("Pool cleaning","Regular visits, reliable results"),("Equipment repair","Pumps, filters, and heaters"),("Green-to-clean","Swamp to swimming"),("Maintenance plans","Protect the investment")],
      badges=["Cleaning + repair","Local operator","Responsive service"],
      phone=None, addr="Sarasota, FL"),
    B(name="EC Service & Moving", theme="steel", word="MOVED", cat="Moving Services",
      tagline="Five-star local moving — pianos and pool tables included.",
      about="EC Service & Moving handles local moves of every kind, including the hard stuff: pianos, office moves, and pool tables. Five-star rated by customers.",
      services=[("Local moving","Careful, insured, on time"),("Piano moving","The move other movers refuse"),("Office relocation","Minimal downtime"),("Pool tables","Leveled and ready to rack")],
      badges=["5-star rated","Specialty items","Sarasota local"],
      phone=None, addr="Sarasota, FL"),
    B(name="Martinez Drywall & Remodeling", theme="steel", word="SMOOTH", cat="Drywall & Remodeling",
      tagline="Clean drywall work, fast responses, free estimates.",
      about="Martinez Drywall & Remodeling delivers quality drywall installation, repair, and remodeling across Sarasota — with fast responses and free estimates.",
      services=[("Installation","New walls, hung and finished"),("Repair & texture","Patches you'll never find"),("Remodeling","Rooms, reimagined"),("Free estimates","Fast answers, fair prices")],
      badges=["Free estimates","Fast response","Registered Florida LLC"],
      phone=None, addr="4523 Olive Ave, Sarasota, FL 34231"),
    B(name="Croz's Surfshack", theme="fiesta", word="ALOHA", cat="Gourmet Hot Dogs & Hawaiian",
      tagline="Gourmet dogs and island flavor since 2014.",
      about="Croz's Surfshack has been rolling through Sarasota and Bradenton since 2014 with gourmet hot dogs and Hawaiian-style plates. Catch the truck — follow us for locations and specials.",
      menu=[("Surf Dogs","Gourmet dogs, loaded island-style"),("Hawaiian Plates","Sweet, savory, aloha on a plate"),("Loaded Sides","Don't skip them"),("Events","Book the shack for your bash")],
      badges=["Est. 2014","Sarasota & Bradenton","Event catering"],
      stats=[("2014","Rolling since"),("2","Counties covered"),("🤙","Aloha guaranteed")],
      phone="(941) 586-3023", addr="Mobile — Sarasota/Bradenton, FL"),
    B(name="Lady Lola Food Truck", theme="fiesta", word="AREPAS", cat="Venezuelan Street Food",
      tagline="Empanadas, pepitos, and Venezuelan street food hecho con amor.",
      about="Lady Lola serves authentic Venezuelan street food — crispy empanadas, loaded pepitos, and more. Order online or find the truck on S Tamiami Trail.",
      menu=[("Empanadas","Crispy, golden, stuffed generously"),("Pepitos","The Venezuelan sandwich that ruins all others"),("Arepas","Griddled fresh, filled to order"),("Tequeños","Cheese sticks the way Caracas makes them")],
      badges=["Authentic Venezuelan","Online ordering","Local favorite"],
      phone="(941) 667-1005", addr="6104 S Tamiami Trl, Sarasota, FL"),
    B(name="Dan Apizz' Man — New Haven Style", theme="fiesta", word="APIZZA", cat="Wood-Fired Pizza",
      tagline="Real New Haven apizza, wood-fired in Sarasota.",
      about="Dan Apizz' Man brings true New Haven-style apizza to Sarasota — charred, thin, and wood-fired. Saturdays at the Sarasota Farmers Market, Wednesday through Friday at Sun King Brewery.",
      menu=[("Original Tomato Pie","The New Haven classic — no mozz needed"),("White Clam Pie","The one people argue about, then order again"),("Pepperoni","Charred edges, cupped roni"),("Private Events","The oven travels")],
      badges=["New Haven style","53 rave reviews","Farmers Market Saturdays"],
      stats=[("900°","Wood-fired heat"),("53","Rave reviews"),("SAT","Farmers Market")],
      hours="Sat @ Farmers Market · Wed–Fri @ Sun King Brewery",
      phone="(516) 476-0699", addr="1215 Mango Ave, Sarasota, FL 34237"),
    B(name="Caribbean BBQ Truck", theme="fiesta", word="SMOKE", cat="Caribbean BBQ & Jerk",
      tagline="Slow smoke. Island spice. Wednesday–Saturday.",
      about="Real Caribbean BBQ and jerk, smoked slow and seasoned right. Find us at 3250 Desoto Rd Wednesday through Saturday, or order on Uber Eats.",
      menu=[("Jerk Chicken","Scotch bonnet heat, real smoke"),("BBQ Plates","Low, slow, islands-meet-South"),("Rice & Peas","The essential side"),("Uber Eats","Delivered hot")],
      badges=["Open Wed–Sat","On Uber Eats","Authentic jerk"],
      hours="Wed–Sat, 3250 Desoto Rd",
      phone="(941) 879-7144", addr="3250 Desoto Rd, Sarasota, FL"),
    B(name="La Cajita SRQ Food Truck", theme="fiesta", word="FUSIÓN", cat="Mexican-Cuban Fusion",
      tagline="Mexican-Cuban fusion, Saturdays at Sun King Brewery.",
      about="La Cajita SRQ blends Mexican and Cuban flavors into one unforgettable menu. Catch us Saturdays at Sun King Brewery or book us for your next event.",
      menu=[("Street Tacos","Mexican soul, Cuban swagger"),("Cuban Classics","Pressed, packed, perfected"),("Fusion Specials","Two islands of flavor, one box"),("Catering","La Cajita at your event")],
      badges=["Fusion menu","Event catering","On Uber Eats"],
      hours="Saturdays @ Sun King Brewery",
      phone=None, addr="Sarasota, FL"),
    B(name="Gran Arepa Southwest", theme="fiesta", word="COLOMBIA", cat="Colombian Street Food",
      tagline="Colombian arepas and empanadas, made fresh in SW Florida.",
      about="Gran Arepa Southwest brings handmade Colombian arepas and empanadas to Sarasota and Southwest Florida. Follow us on Instagram for locations.",
      menu=[("Arepas con Queso","Griddled corn, melted cheese"),("Empanadas","Golden and crisp, Colombian-style"),("Street Plates","Hearty and handmade"),("Events","Bring Colombia to your party")],
      badges=["Handmade daily","Sarasota/SW FL","Follow on Instagram"],
      phone=None, addr="Mobile — Sarasota/SW Florida"),
    B(name="Phatheadz Barbershop", theme="barber", word="NEWTOWN", cat="Barbershop",
      tagline="Serving Newtown since 2008. Book online in seconds.",
      about="Phatheadz Barbershop has served the Newtown community since 2008. Minority-owned, Chamber member, and easy to book — fades, tapers, designs, and more.",
      services=[("Fades & tapers","Clean every time"),("Designs & lineups","Precision work"),("Beard work","Shaped and sharp"),("Online booking","Book on Booksy in seconds")],
      badges=["Since 2008","Minority-owned","Chamber member"],
      stats=[("2008","Serving Newtown since"),("★★★★★","Booksy rated"),("SRQ","Chamber member")],
      phone="(941) 917-0329", addr="1818 Dr Martin Luther King Jr Way, Sarasota, FL 34234"),
    B(name="5STAR Barbershop", theme="barber", word="★★★★★", cat="Barbershop",
      tagline="4.9 stars. The name says it all.",
      about="5STAR Barbershop lives up to the name — 4.9 stars across dozens of reviews. Book online and get a cut that earns its rating.",
      services=[("Cuts & fades","Rated 4.9 for a reason"),("Beard trims","Finished properly"),("Kids' cuts","Quick and painless"),("Online booking","Booksy & Fresha")],
      badges=["4.9★ rating","Online booking","Sarasota local"],
      stats=[("4.9★","Average rating"),("69+","Booksy reviews"),("5","Stars in the name")],
      phone=None, addr="3050 17th St, Sarasota, FL 34234"),
    B(name="Pat's Barbershop", theme="barber", word="CLASSIC", cat="Barbershop",
      tagline="Old-fashioned barbershop with modern flair.",
      about="Pat's Barbershop blends old-school barbering tradition with modern style. Classic cuts, hot lather, and conversation worth the chair time.",
      services=[("Classic cuts","Timeless, tailored"),("Modern styles","Current without trying too hard"),("Beard & shave","Hot lather service"),("Walk-ins","And appointments too")],
      badges=["Old-school tradition","Modern styles","Neighborhood staple"],
      phone="(941) 365-5441", addr="935 N Beneva Rd Ste 615, Sarasota, FL"),
    B(name="Cattlemen Barber Shop", theme="barber", word="WALK IN", cat="Barbershop",
      tagline="Four chairs, no fuss. Walk-ins welcome since 2009.",
      about="Cattlemen Barber Shop is a four-chair, walk-in-friendly shop that's been cutting Sarasota's hair since 2009. Licensed, quick, and consistent.",
      services=[("Men's cuts","Consistent, quick, right"),("Flat tops & fades","Old school done well"),("Seniors & kids","Everyone's welcome"),("Walk-ins","No appointment needed")],
      badges=["Est. 2009","Walk-ins welcome","FL licensed"],
      stats=[("2009","Cutting since"),("4","Chairs, no wait games"),("FL","Licensed shop")],
      phone="(941) 377-6611", addr="999 Cattlemen Rd Unit D, Sarasota, FL 34232"),
    B(name="Gulf Gate Barbershop", theme="barber", word="GULF GATE", cat="Barbershop",
      tagline="Your neighborhood barbershop in Gulf Gate.",
      about="Gulf Gate Barbershop keeps the neighborhood looking sharp — quality cuts in the heart of Gulf Gate, without the wait or the price tag.",
      services=[("Haircuts","Neighborhood quality"),("Fades & tapers","Done properly"),("Beard trims","Cleaned up"),("Book on Fresha","Or just walk in")],
      badges=["Gulf Gate local","Book on Fresha","Neighborhood prices"],
      phone=None, addr="6575 Gateway Ave, Sarasota, FL 34231"),
    B(name="Family Hair Salon & Barber Shop", theme="blush", word="FAMILIA", cat="Family Salon & Barbershop",
      tagline="Cuts, color, and nails for the whole family.",
      about="One stop for the whole family — men's and women's cuts, kids' cuts, color, and nails. Freshly remodeled under new ownership on Bee Ridge Road.",
      services=[("Kids' cuts","Patient and fun"),("Men's & women's cuts","Everyone leaves happy"),("Color","Full color services"),("Nails","Finish the look")],
      badges=["Whole-family services","Newly remodeled","Bee Ridge Rd"],
      phone=None, addr="4517 Bee Ridge Rd, Sarasota, FL 34233"),
    B(name="TT Nails Spa", theme="blush", word="POLISH", cat="Nail Salon",
      tagline="Walk-ins welcome. Women-owned. Beautifully done.",
      about="TT Nails Spa is a women-owned salon where walk-ins are always welcome. Manicures, pedicures, and nail art done with care.",
      services=[("Manicures","Clean, precise, lasting"),("Pedicures","Relax, it's handled"),("Gel & dip","Durable and glossy"),("Nail art","Your idea, our hands")],
      badges=["Women-owned","Walk-ins welcome","Lockwood Ridge"],
      phone="(941) 359-1117", addr="6370 N Lockwood Ridge Rd, Sarasota, FL 34243"),
    B(name="Pink Petals Nail Spa", theme="blush", word="PETALS", cat="Nail Salon",
      tagline="4.9 stars across 687 reviews — and counting.",
      about="Pink Petals Nail Spa has earned 4.9 stars across nearly 700 reviews. Impeccable manicures, relaxing pedicures, and a spotless studio near University Parkway.",
      services=[("Mani & pedi","The full treatment"),("Gel, dip & acrylic","Every finish, done well"),("Spa treatments","Actually relaxing"),("Groups","Bring the party")],
      badges=["4.9★ / 687 reviews","University Pkwy","Book on Fresha"],
      stats=[("4.9★","Average rating"),("687","Reviews"),("💅","Worth every one")],
      phone="(941) 358-3851", addr="3315 University Pkwy #102, Sarasota, FL 34243"),
    B(name="Valentine's Nail Spa", theme="blush", word="AMOUR", cat="Nail Salon",
      tagline="The busy little nail spa on the South Trail.",
      about="Valentine's Nail Spa is a South Tamiami Trail favorite — busy for a reason. Quality sets, friendly techs, fair prices.",
      services=[("Full sets","Built to last"),("Mani & pedi","The classics, done right"),("Gel & designs","Something to show off"),("Waxing","Quick and clean")],
      badges=["79+ reviews","South Trail","Fair prices"],
      phone="(941) 922-8282", addr="7350 S Tamiami Trl, Sarasota, FL 34231"),
    B(name="Kelly's Private Home Dog Grooming", theme="paws", word="GENTLE", cat="Dog Grooming",
      tagline="Calm, private, one-on-one grooming for small dogs.",
      about="15 years of grooming experience in a calm, private home setting — no cages, no chaos. Specializing in small dogs, by appointment.",
      services=[("Small-dog grooming","Gentle, unhurried, thorough"),("Bath & tidy","Fresh without the full works"),("Private setting","One dog at a time"),("By appointment","Your dog gets the whole session")],
      badges=["15 years experience","Private home studio","Small-dog specialist"],
      stats=[("15","Years of grooming"),("1","Dog at a time"),("0","Cages, ever")],
      phone="(941) 284-4083", addr="Bahia Vista area, Sarasota, FL"),
    B(name="Shaggy Companions", theme="paws", word="WALKIES", cat="Pet Sitting & Dog Walking",
      tagline="Tailored in-home pet care while you're away.",
      about="Shaggy Companions provides personalized in-home pet sitting and dog walking across Sarasota — your pets keep their routine, you keep your peace of mind.",
      services=[("In-home sitting","Their house, their rules"),("Dog walking","Rain or shine"),("Vacation visits","Photos included"),("Custom plans","Built around your pet")],
      badges=["In-home care","Custom plans","Sarasota local"],
      phone=None, addr="Sarasota, FL"),
    B(name="Lesley's Pet Sitters", theme="paws", word="TRUSTED", cat="Pet Sitting & Dog Walking",
      tagline="Top-12 rated pet care for Sarasota, Bradenton & Venice.",
      about="Lesley's Pet Sitters offers in-home care, walks, and medication visits with a 100% recommendation rate — rated among the area's top 12 pet sitters.",
      services=[("In-home sitting","Comfort of home"),("Dog walking","Daily or as needed"),("Medication visits","Experienced with meds"),("3 cities","Sarasota, Bradenton & Venice")],
      badges=["100% recommended","Top-12 area rating","Meds experience"],
      stats=[("100%","Recommend rate"),("Top 12","Area ranking"),("3","Cities served")],
      phone="(941) 228-3209", addr="33 S Gulfstream Ave, Sarasota, FL 34236"),
    B(name="Rare Auto Detailing", theme="ink", word="SHINE", cat="Mobile Auto Detailing",
      tagline="Certified ceramic coating and tint — we come to you.",
      about="Rare Auto Detailing is IGL Ceramic and MAXPRO Tint certified, bringing showroom-level detailing, coatings, and tint straight to your driveway.",
      services=[("Full detailing","Showroom finish, your driveway"),("Ceramic coating","IGL certified application"),("Window tint","MAXPRO certified installs"),("Mobile","We come to you")],
      badges=["IGL certified","MAXPRO certified","100% recommended"],
      stats=[("2","Pro certifications"),("100%","Recommend rate"),("0","Miles you drive")],
      phone="(941) 914-8102", addr="Mobile — Sarasota, FL"),
    B(name="American Pie Antiques & Collectibles", theme="vintage", word="ANTIQUE", cat="Antiques & Collectibles",
      tagline="Downtown Sarasota's treasure chest on Fruitville Road.",
      about="American Pie Antiques & Collectibles is packed with finds — vintage Americana, collectibles, and one-of-a-kind pieces in downtown Sarasota.",
      services=[("Antiques & vintage","Curated, not cluttered"),("Collectibles","From kitsch to classic"),("Americana","History you can hold"),("New finds weekly","Worth the repeat visit")],
      badges=["Downtown Sarasota","One-of-a-kind finds","Browse-worthy"],
      phone="(941) 362-0682", addr="1470 Fruitville Rd, Sarasota, FL 34236"),
    B(name="Suncoast Auto Repair of Sarasota", theme="ink", word="TORQUE", cat="Auto Repair",
      tagline="Honest auto repair on 17th Street.",
      about="Suncoast Auto Repair of Sarasota is an independent, BBB-listed shop doing honest diagnostic and repair work — the neighborhood alternative to dealership prices.",
      services=[("Diagnostics","Find it, explain it, fix it"),("Brakes & suspension","Safety first"),("Engine & transmission","The big jobs, handled"),("Maintenance","Scheduled service, no upsell")],
      badges=["Independent shop","BBB listed","Active FL LLC"],
      phone="(941) 954-6097", addr="2221 17th St, Sarasota, FL 34234"),
    B(name="The Bike Shop", theme="fresh", word="RIDE", cat="Bicycle Sales & Repair",
      tagline="Sales, service, and straight answers on McIntosh Road.",
      about="The Bike Shop keeps Sarasota riding — tune-ups, repairs, and bikes without the big-box attitude.",
      services=[("Tune-ups","Smooth and silent again"),("Repairs","Fixed, not replaced"),("Bike sales","Honest recommendations"),("Parts & accessories","What you actually need")],
      badges=["Local shop","McIntosh Rd","Service first"],
      phone="(941) 404-9090", addr="5444 McIntosh Rd, Sarasota, FL 34232"),
    B(name="Sooper Dooper Bikes", theme="fresh", word="ROLLING", cat="Mobile Bike Repair",
      tagline="20+ years of bike repair — delivered to your door.",
      about="Sooper Dooper Bikes brings 20+ years of repair experience to you, with regular stops across Sarasota and Manatee counties — Longboat Key, West Bradenton, and more. Call or text.",
      services=[("Mobile repair","The shop comes to you"),("Tune-ups","At your door"),("Neighborhood stops","Regular routes"),("Call or text","Easy booking")],
      badges=["20+ years experience","Mobile service","Sarasota & Manatee"],
      stats=[("20+","Years wrenching"),("2","Counties covered"),("0","Trips to a shop")],
      phone="(941) 289-7861", addr="Mobile — Sarasota & Manatee counties"),
    B(name="Manasota Mobile Marine", theme="ocean", word="DOCKSIDE", cat="Mobile Boat & Outboard Repair",
      tagline="Certified outboard repair that comes to your dock.",
      about="Manasota Mobile Marine is a certified outboard specialist serving Sarasota and Manatee counties — repairs and maintenance at your dock, lift, or driveway.",
      services=[("Outboard repair","Certified specialist work"),("Dockside service","Your dock, lift, or driveway"),("Maintenance","Winterizing and upkeep"),("Two counties","Sarasota & Manatee")],
      badges=["Certified outboard specialist","We come to you","Two-county coverage"],
      phone="(941) 745-1444", addr="Mobile — Sarasota & Manatee counties"),
]

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{name} — {cat} · Sarasota, FL</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={gfonts}&display=swap" rel="stylesheet">
<style>
:root {{
  --h1:{h1}; --h2:{h2}; --glow:{glow}; --bg:{bg}; --ink:{ink}; --card:{card};
  --ac:{ac}; --ac2:{ac2}; --display:{dfont}; --body:'Inter',-apple-system,'Segoe UI',Roboto,sans-serif;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ font-family:var(--body); background:var(--bg); color:var(--ink); line-height:1.65; -webkit-font-smoothing:antialiased; }}
.demo {{ background:#0a0a0a; color:#e5e5e5; font-size:.72rem; text-align:center; padding:.4rem .8rem; letter-spacing:.06em; text-transform:uppercase; }}
.demo b {{ color:var(--ac2); }}
nav {{ position:sticky; top:0; z-index:50; display:flex; align-items:center; justify-content:space-between; gap:1rem;
  padding:.7rem clamp(1rem,4vw,2.5rem); background:color-mix(in srgb,var(--h1) 92%,transparent); backdrop-filter:blur(10px); color:#fff; }}
.logotype {{ font-family:var(--display); font-size:1.05rem; letter-spacing:.04em; display:flex; align-items:center; gap:.6rem; text-decoration:none; color:#fff; }}
.mono {{ width:2.1rem; height:2.1rem; border-radius:8px; background:linear-gradient(135deg,var(--ac2),var(--ac)); color:var(--h1);
  display:grid; place-items:center; font-family:var(--display); font-size:1.05rem; }}
nav .navcall {{ font-weight:700; font-size:.88rem; color:var(--h1); background:var(--ac2); padding:.5rem 1.1rem; border-radius:999px; text-decoration:none; white-space:nowrap; }}
/* HERO */
.hero {{ position:relative; overflow:hidden; color:#fff; background:
  radial-gradient(60rem 32rem at 85% -10%, color-mix(in srgb,var(--glow) 32%,transparent), transparent 60%),
  radial-gradient(40rem 30rem at -10% 110%, color-mix(in srgb,var(--glow) 18%,transparent), transparent 55%),
  linear-gradient(150deg,var(--h1) 20%,var(--h2)); }}
.hero::before {{ content:""; position:absolute; inset:0; background-image:url("{noise}"); opacity:.35; mix-blend-mode:overlay; pointer-events:none; }}
.hero .wm {{ position:absolute; right:-1rem; bottom:-1.2rem; font-family:var(--display); font-size:clamp(5rem,17vw,13rem);
  line-height:.8; color:transparent; -webkit-text-stroke:1.5px color-mix(in srgb,#fff 22%,transparent); letter-spacing:.02em; user-select:none; pointer-events:none; white-space:nowrap; }}
.hero-in {{ position:relative; max-width:68rem; margin:0 auto; padding:clamp(4rem,9vw,7.5rem) clamp(1.25rem,4vw,2.5rem) clamp(5rem,10vw,8rem); }}
.eyebrow {{ display:inline-flex; align-items:center; gap:.55rem; text-transform:uppercase; letter-spacing:.22em; font-size:.74rem; font-weight:600; opacity:.9; margin-bottom:1.3rem; }}
.eyebrow::before {{ content:""; width:2.2rem; height:2px; background:var(--ac2); }}
.hero h1 {{ font-family:var(--display); font-size:clamp(2.6rem,7.5vw,5.2rem); line-height:1.02; letter-spacing:-.01em; max-width:16ch; margin-bottom:1.1rem; }}
.hero p.tag {{ font-size:clamp(1.05rem,2.3vw,1.35rem); max-width:38ch; opacity:.92; margin-bottom:2.2rem; }}
.ctas {{ display:flex; flex-wrap:wrap; gap:.8rem; }}
.btn {{ display:inline-flex; align-items:center; gap:.5rem; font-weight:700; padding:.95rem 1.8rem; border-radius:999px; text-decoration:none; font-size:1rem; }}
.btn.primary {{ background:var(--ac2); color:var(--h1); box-shadow:0 10px 30px color-mix(in srgb,var(--glow) 45%,transparent); }}
.btn.ghost {{ color:#fff; border:1.5px solid rgba(255,255,255,.45); }}
.trust {{ display:flex; flex-wrap:wrap; gap:.5rem 1.6rem; margin-top:3rem; font-size:.86rem; opacity:.9; }}
.trust span {{ display:inline-flex; align-items:center; gap:.5rem; }}
.trust span::before {{ content:"◆"; font-size:.6rem; color:var(--ac2); }}
.wave {{ display:block; width:100%; height:4.5rem; margin-top:-4.4rem; position:relative; }}
/* SECTIONS */
main {{ max-width:68rem; margin:0 auto; padding:0 clamp(1.25rem,4vw,2.5rem) 4rem; }}
section {{ padding-top:clamp(3rem,7vw,5rem); }}
.kicker {{ text-transform:uppercase; letter-spacing:.2em; font-size:.72rem; font-weight:700; color:var(--ac); margin-bottom:.5rem; }}
h2 {{ font-family:var(--display); font-size:clamp(1.7rem,3.8vw,2.5rem); line-height:1.1; margin-bottom:1.2rem; letter-spacing:-.01em; }}
.about-grid {{ display:grid; grid-template-columns:1fr; gap:1.5rem; }}
@media(min-width:760px) {{ .about-grid {{ grid-template-columns:1.1fr .9fr; align-items:center; gap:3rem; }} }}
.about-grid p {{ font-size:1.06rem; }}
.stats {{ display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:color-mix(in srgb,var(--ink) 12%,transparent);
  border-radius:16px; overflow:hidden; box-shadow:0 14px 40px rgba(0,0,0,.08); }}
.stat {{ background:var(--h1); color:#fff; padding:1.5rem 1rem; text-align:center; }}
.stat .n {{ font-family:var(--display); font-size:clamp(1.5rem,3.5vw,2.2rem); color:var(--ac2); display:block; line-height:1.1; }}
.stat .l {{ font-size:.76rem; opacity:.85; margin-top:.3rem; display:block; }}
.cards {{ display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(15rem,1fr)); margin-top:1.6rem; }}
.cardx {{ background:var(--card); border-radius:16px; padding:1.5rem 1.4rem; box-shadow:0 8px 26px rgba(0,0,0,.06);
  border-top:3px solid var(--ac2); }}
.cardx h3 {{ font-family:var(--display); font-size:1.12rem; margin-bottom:.35rem; letter-spacing:.01em; }}
.cardx p {{ font-size:.92rem; opacity:.82; }}
.cardx .num {{ font-family:var(--display); color:color-mix(in srgb,var(--ac) 34%,transparent); font-size:.95rem; display:block; margin-bottom:.6rem; }}
/* MENU variant */
.menu-list {{ margin-top:1.6rem; display:grid; gap:0; background:var(--card); border-radius:18px; overflow:hidden; box-shadow:0 10px 30px rgba(0,0,0,.07); }}
.dish {{ display:flex; justify-content:space-between; gap:1.5rem; padding:1.35rem 1.6rem; border-bottom:1px dashed color-mix(in srgb,var(--ink) 18%,transparent); }}
.dish:last-child {{ border-bottom:none; }}
.dish h3 {{ font-family:var(--display); font-size:1.15rem; }}
.dish p {{ font-size:.92rem; opacity:.8; }}
.dish .dot {{ align-self:center; color:var(--ac2); font-size:1.3rem; }}
/* CONTACT */
.contact {{ margin-top:clamp(3rem,7vw,5rem); border-radius:22px; overflow:hidden; display:grid; grid-template-columns:1fr;
  box-shadow:0 20px 50px rgba(0,0,0,.14); }}
@media(min-width:760px) {{ .contact {{ grid-template-columns:1.1fr .9fr; }} }}
.contact .left {{ background:linear-gradient(150deg,var(--h1),var(--h2)); color:#fff; padding:clamp(2rem,5vw,3.2rem); position:relative; overflow:hidden; }}
.contact .left::before {{ content:""; position:absolute; inset:0; background-image:url("{noise}"); opacity:.3; mix-blend-mode:overlay; }}
.contact .left h2 {{ color:#fff; }}
.bigphone {{ font-family:var(--display); font-size:clamp(1.6rem,4.5vw,2.6rem); color:var(--ac2); text-decoration:none; display:inline-block; margin:.6rem 0 1rem; position:relative; }}
.contact .right {{ background:var(--card); padding:clamp(2rem,5vw,3.2rem); display:flex; flex-direction:column; gap:1.2rem; justify-content:center; }}
.crow {{ display:flex; gap:.9rem; align-items:flex-start; }}
.crow svg {{ flex:none; width:1.3rem; height:1.3rem; stroke:var(--ac); fill:none; stroke-width:2; margin-top:.2rem; }}
.crow .lbl {{ text-transform:uppercase; font-size:.68rem; letter-spacing:.16em; opacity:.6; }}
footer {{ text-align:center; font-size:.78rem; padding:2.2rem 1.25rem 5.5rem; opacity:.65; max-width:46rem; margin:0 auto; }}
.callbar {{ position:fixed; left:0; right:0; bottom:0; z-index:60; display:none; padding:.7rem 1rem calc(.7rem + env(safe-area-inset-bottom));
  background:color-mix(in srgb,var(--h1) 94%,transparent); backdrop-filter:blur(8px); }}
.callbar a {{ display:block; text-align:center; background:var(--ac2); color:var(--h1); font-weight:800; padding:.85rem; border-radius:12px; text-decoration:none; }}
@media(max-width:700px) {{ .callbar.has {{ display:block; }} nav .navcall {{ display:none; }} }}
</style>
</head>
<body>
<div class="demo"><b>Concept demo</b> — proposal mockup, not the official site of {name}</div>
<nav>
  <a class="logotype" href="#"><span class="mono">{initial}</span>{shortname}</a>
  {navcall}
</nav>
<header class="hero">
  <div class="wm">{word}</div>
  <div class="hero-in">
    <div class="eyebrow">{cat} · Sarasota, FL</div>
    <h1>{headline}</h1>
    <p class="tag">{tagline}</p>
    <div class="ctas">{cta_primary}<a class="btn ghost" href="#services">{secondary_label}</a></div>
    <div class="trust">{trust}</div>
  </div>
  <svg class="wave" viewBox="0 0 1440 90" preserveAspectRatio="none"><path d="M0,64 C240,96 480,16 720,40 C960,64 1200,88 1440,48 L1440,90 L0,90 Z" fill="{bg}"/></svg>
</header>
<main>
{stats_html}
<section class="about-grid" id="about">
  <div>
    <div class="kicker">Who we are</div>
    <h2>{about_h}</h2>
    <p>{about}</p>
  </div>
  <div>{about_side}</div>
</section>
<section id="services">
  <div class="kicker">{svc_kicker}</div>
  <h2>{svc_h}</h2>
  {svc_html}
</section>
<section class="contact" id="contact">
  <div class="left">
    <div class="kicker" style="color:var(--ac2)">Get in touch</div>
    <h2>{contact_h}</h2>
    {phone_html}
    <p style="opacity:.85">{addr}</p>
  </div>
  <div class="right">
    <div class="crow"><svg viewBox="0 0 24 24"><path d="M12 21s-7-5.5-7-11a7 7 0 1 1 14 0c0 5.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>
      <div><div class="lbl">Find us</div><div>{addr}</div></div></div>
    {hours_row}
    {phone_row}
  </div>
</section>
</main>
<footer>Concept website mockup generated for pitch purposes. Business details compiled from public listings and should be verified with the owner before publication. This page is not affiliated with or approved by {name}.</footer>
{callbar}
</body>
</html>
"""

def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)

def shortname(name):
    return name if len(name) <= 26 else name[:24].rsplit(" ", 1)[0] + "…"

def build():
    e = html.escape
    cards = []
    for b in BUSINESSES:
        slug = slugify(b["name"])
        t = THEMES[b["theme"]]
        dfont, gfonts = FONTS[t["font"]]
        phone = b.get("phone")
        tel = re.sub(r"\D", "", phone) if phone else ""
        is_menu = "menu" in b

        cta_primary = (f'<a class="btn primary" href="tel:{tel}">Call {e(phone)}</a>' if phone
                       else '<a class="btn primary" href="#contact">Get in touch</a>')
        navcall = (f'<a class="navcall" href="tel:{tel}">{e(phone)}</a>' if phone
                   else '<a class="navcall" href="#contact">Contact</a>')
        callbar = (f'<div class="callbar has"><a href="tel:{tel}">📞 Tap to call {e(phone)}</a></div>' if phone else '<div class="callbar"></div>')

        if b.get("stats"):
            stats_html = ('<section class="stats" style="padding-top:0;margin-top:2.2rem">' +
                "".join(f'<div class="stat"><span class="n">{e(n)}</span><span class="l">{e(l)}</span></div>'
                        for n, l in b["stats"]) + "</section>")
        else:
            stats_html = ""

        if is_menu:
            svc_kicker, svc_h, secondary_label = "The food", "Menu highlights", "See the menu"
            svc_html = ('<div class="menu-list">' +
                "".join(f'<div class="dish"><div><h3>{e(n)}</h3><p>{e(d)}</p></div><span class="dot">✦</span></div>'
                        for n, d in b["menu"]) + "</div>")
        else:
            svc_kicker, svc_h, secondary_label = "What we do", "Services", "Our services"
            svc_html = ('<div class="cards">' +
                "".join(f'<div class="cardx"><span class="num">0{i+1}</span><h3>{e(n)}</h3><p>{e(d)}</p></div>'
                        for i, (n, d) in enumerate(b["services"])) + "</div>")

        about_side = ('<div class="cards" style="margin-top:0">' +
            "".join(f'<div class="cardx" style="border-top-color:var(--ac)"><h3 style="font-size:.98rem">{e(x)}</h3></div>'
                    for x in b["badges"]) + "</div>")

        phone_html = (f'<a class="bigphone" href="tel:{tel}">{e(phone)}</a>' if phone
                      else '<p class="bigphone" style="font-size:1.2rem">Message us on our social pages</p>')
        phone_row = (f'<div class="crow"><svg viewBox="0 0 24 24"><path d="M4 5c0 8 7 15 15 15l2-4-4.5-2-2 2c-2.5-1.2-4.3-3-5.5-5.5l2-2L9 4z"/></svg>'
                     f'<div><div class="lbl">Call</div><a href="tel:{tel}" style="color:var(--ac);font-weight:700">{e(phone)}</a></div></div>') if phone else ""
        hours_row = (f'<div class="crow"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></svg>'
                     f'<div><div class="lbl">Hours</div><div>{e(b["hours"])}</div></div></div>') if b.get("hours") else ""

        first_word = b["name"].split()[0].rstrip("'s,")
        page = PAGE.format(
            name=e(b["name"]), cat=e(b["cat"]), tagline=e(b["tagline"]), about=e(b["about"]),
            headline=e(b["name"]), word=e(b["word"]), initial=e(b["name"][0]),
            shortname=e(shortname(b["name"])), addr=e(b["addr"]),
            about_h=f"{e(first_word)}, at your service." if not is_menu else "Come hungry.",
            contact_h="Let’s talk." if not is_menu else "Find us. Feed yourself.",
            cta_primary=cta_primary, navcall=navcall, callbar=callbar, stats_html=stats_html,
            svc_kicker=svc_kicker, svc_h=svc_h, svc_html=svc_html, secondary_label=secondary_label,
            about_side=about_side, phone_html=phone_html, phone_row=phone_row, hours_row=hours_row,
            trust="".join(f"<span>{e(x)}</span>" for x in b["badges"]),
            gfonts=gfonts, dfont=dfont, noise=NOISE,
            h1=t["h1"], h2=t["h2"], glow=t["glow"], bg=t["bg"], ink=t["ink"], card=t["card"], ac=t["ac"], ac2=t["ac2"],
        )
        d = os.path.join(ROOT, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(page)
        cards.append((slug, b))

    items = "".join(
        f'<a class="tile" href="{slug}/index.html" style="--g:linear-gradient(150deg,{THEMES[b["theme"]]["h1"]},{THEMES[b["theme"]]["h2"]});--a:{THEMES[b["theme"]]["ac2"]}">'
        f'<div class="hero"><span>{html.escape(b["word"])}</span></div>'
        f'<div class="body"><h3>{html.escape(b["name"])}</h3><p>{html.escape(b["cat"])}</p></div></a>'
        for slug, b in cards)
    gallery = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Sarasota Demo Sites — {len(cards)} concepts</title>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Inter',-apple-system,sans-serif; background:#0f1115; color:#e7e7ea; padding:3rem 1.25rem 4rem; }}
h1 {{ font-family:'Archivo Black',sans-serif; text-align:center; font-size:clamp(1.8rem,5vw,3rem); margin-bottom:.4rem; }}
p.sub {{ text-align:center; opacity:.6; margin-bottom:2.5rem; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(15rem,1fr)); gap:1.1rem; max-width:74rem; margin:0 auto; }}
.tile {{ background:#181b21; border-radius:14px; overflow:hidden; text-decoration:none; color:inherit; transition:transform .12s; border:1px solid #262a33; }}
.tile:hover {{ transform:translateY(-3px); border-color:var(--a); }}
.tile .hero {{ background:var(--g); min-height:5.6rem; display:grid; place-items:center; }}
.tile .hero span {{ font-family:'Archivo Black',sans-serif; color:transparent; -webkit-text-stroke:1px var(--a); font-size:1.5rem; letter-spacing:.05em; }}
.tile .body {{ padding:.9rem 1rem 1.1rem; }}
.tile h3 {{ font-size:.95rem; margin-bottom:.15rem; }}
.tile p {{ font-size:.78rem; opacity:.55; }}
</style></head><body>
<h1>Sarasota Concept Sites</h1>
<p class="sub">{len(cards)} pitch-ready one-page concepts — click any tile to preview</p>
<div class="grid">{items}</div>
</body></html>"""
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(gallery)
    print(f"Built {len(cards)} demo sites + gallery")

if __name__ == "__main__":
    build()
