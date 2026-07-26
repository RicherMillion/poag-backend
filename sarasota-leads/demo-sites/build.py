#!/usr/bin/env python3
"""Generate one-page concept demo websites for Sarasota no-website leads.

Each site is a self-contained index.html (inline CSS, system fonts, no
external requests) under demo-sites/<slug>/. Also builds a gallery
index.html listing every demo. Re-run after editing BUSINESSES.
"""
import os, re, html

ROOT = os.path.dirname(os.path.abspath(__file__))

THEMES = {
    # key: (bg, surface, ink, accent, accent2, hero_emoji_bg)
    "ocean":   ("#f0f7fa", "#ffffff", "#0b3954", "#0e7490", "#00a8cc", "linear-gradient(135deg,#0b3954,#0e7490)"),
    "fresh":   ("#f3faf4", "#ffffff", "#14532d", "#16a34a", "#84cc16", "linear-gradient(135deg,#14532d,#16a34a)"),
    "steel":   ("#f4f6f8", "#ffffff", "#1e293b", "#b91c1c", "#f59e0b", "linear-gradient(135deg,#1e293b,#475569)"),
    "barber":  ("#f7f6f3", "#ffffff", "#111827", "#a16207", "#d4af37", "linear-gradient(135deg,#111827,#374151)"),
    "blush":   ("#fdf2f8", "#ffffff", "#831843", "#be185d", "#f472b6", "linear-gradient(135deg,#831843,#be185d)"),
    "paws":    ("#f0fdfa", "#ffffff", "#134e4a", "#0f766e", "#2dd4bf", "linear-gradient(135deg,#134e4a,#0f766e)"),
    "vintage": ("#faf6f0", "#ffffff", "#451a03", "#92400e", "#d97706", "linear-gradient(135deg,#451a03,#92400e)"),
    "ink":     ("#f5f5f5", "#ffffff", "#171717", "#b91c1c", "#dc2626", "linear-gradient(135deg,#171717,#404040)"),
    "fiesta":  ("#fffbeb", "#ffffff", "#7f1d1d", "#c2410c", "#fbbf24", "linear-gradient(135deg,#7f1d1d,#c2410c)"),
}

B = lambda **kw: kw
BUSINESSES = [
    # --- Hot: dead/broken domains ---
    B(name="Dominion Exterminators", theme="steel", emoji="🐜", cat="Pest Control",
      tagline="Family-owned pest control, trusted in Sarasota for decades.",
      about="Dominion Exterminators is a family owned and operated pest control company serving Sarasota. Neighbors on Nextdoor have trusted us for years for thorough, honest work at reasonable prices — many customers have been with us for 15+ years.",
      services=["Rodent control", "Cockroach extermination", "General pest control", "Preventive treatment plans"],
      badges=["Family owned & operated", "15+ year repeat customers", "Nextdoor Neighborhood Favorite"],
      phone="(941) 266-6659", addr="2116 Bay St, Sarasota, FL 34237"),
    B(name="Walt's Marine Service", theme="ocean", emoji="⚓", cat="Marine & Boat Repair",
      tagline="35+ years keeping Sarasota's boats on the water.",
      about="Walt's Marine Service has served Sarasota boaters for more than 35 years. From routine maintenance to major repairs, bring your boat to a shop with decades of hands-on experience.",
      services=["Engine service & repair", "Routine maintenance", "Electrical & systems", "Haul-out & seasonal prep"],
      badges=["35+ years in business", "Local & independent", "Trusted by Sarasota boaters"],
      phone="(941) 955-6785", addr="2073 20th St, Sarasota, FL 34234"),
    B(name="Jamaican American Soul Food", theme="fiesta", emoji="🍗", cat="Jamaican & Soul Food Restaurant",
      tagline="Real jerk. Real soul. Right on Dr. MLK Jr. Way.",
      about="Authentic Jamaican and Southern soul food cooked the way it should be. Order for pickup or delivery — we're on DoorDash and Grubhub — or come by the restaurant.",
      services=["Jerk chicken & pork", "Oxtail & curry goat", "Southern soul food plates", "Delivery via DoorDash & Grubhub"],
      badges=["Authentic island recipes", "Open for takeout & delivery", "Sarasota local favorite"],
      phone="(941) 260-5723", addr="2025 Dr Martin Luther King Jr Way, Sarasota, FL 34234"),
    B(name="SRQ Marine Services, LLC", theme="ocean", emoji="🛥️", cat="Boat Restoration & Repair",
      tagline="Restoration, repower, and repair — done right in Sarasota.",
      about="SRQ Marine Services handles everything from motor maintenance and repowers to full restorations, plus transportation and delivery. Skilled, honest marine work by people who live on this water.",
      services=["Motor maintenance & repower", "Boat restoration", "Transportation & delivery", "General marine repair"],
      badges=["Full-service marine shop", "Restoration specialists", "Local Sarasota crew"],
      phone="(941) 685-9434", addr="510 Mango Ave, Sarasota, FL 34237"),
    # --- High value ---
    B(name="Messenger's Barber Shop & Beauty Salon", theme="barber", emoji="💈", cat="Barber Shop & Beauty Salon",
      tagline="Three generations of cuts. Serving Sarasota since 1964.",
      about="A third-generation family business, Messenger's has been cutting hair in Sarasota since 1964. Classic barbering and full salon services, with 4.8 stars from the neighbors we've served for decades.",
      services=["Men's cuts & fades", "Women's styling", "Kids' cuts", "Beard trims & shaves"],
      badges=["Since 1964", "3rd-generation family business", "4.8★ customer rating"],
      phone="(941) 366-3677", addr="3251 17th St #70, Sarasota, FL 34235"),
    B(name="JB SRQ Handyman Services", theme="steel", emoji="🔨", cat="Handyman Services",
      tagline="38 years of fixing it right the first time.",
      about="JB SRQ Handyman Services brings 38 years of experience to every job — repairs, installs, and the punch list you've been putting off. A Nextdoor Neighborhood Favorite, BBB-listed and Sarasota through and through.",
      services=["Home repairs", "Fixture & appliance installs", "Carpentry & trim", "Punch-list projects"],
      badges=["38 years in business", "Nextdoor Favorite 2022 & 2023", "BBB profile"],
      phone="(941) 228-7763", addr="2737 Hyde Park St, Sarasota, FL 34239"),
    B(name="Economy Lock & Key", theme="steel", emoji="🔑", cat="Locksmith",
      tagline="Sarasota's trusted locksmith since 1987.",
      about="Economy Lock & Key has kept Sarasota homes and businesses secure since 1987. BBB accredited, independent, and local — call for lockouts, rekeys, and hardware.",
      services=["Lockouts", "Rekeying", "Lock installation & repair", "Commercial hardware"],
      badges=["Since 1987", "BBB accredited", "Local & independent"],
      phone="(941) 377-8237", addr="5317 Fruitville Rd, Sarasota, FL 34232"),
    B(name="Rose and Dagger Tattoo Studio", theme="ink", emoji="🗡️", cat="Tattoo Studio",
      tagline="The only tattoo studio on Siesta Key.",
      about="Custom tattoos steps from the #1 beach in America. Rose and Dagger is Siesta Key's only tattoo studio — walk-ins and appointments, clean work, island atmosphere.",
      services=["Custom tattoos", "Walk-ins welcome", "Cover-ups & reworks", "Flash & souvenir pieces"],
      badges=["Only studio on Siesta Key", "Active on Instagram", "Tourist & local favorite"],
      phone="(941) 893-9917", addr="5111 Ocean Blvd Ste H, Siesta Key, FL 34242"),
    B(name="Baja Boys Grill", theme="fiesta", emoji="🌮", cat="Taco Truck",
      tagline="Voted Best Food Truck in SRQ.",
      about="Baja-style tacos and burritos out of the Rosemary District. Voted best food truck in Sarasota — find the truck, grab a taco, thank us later.",
      services=["Baja fish tacos", "Burritos & bowls", "Catering & events", "Follow the truck on socials"],
      badges=["Best Food Truck in SRQ", "Rosemary District", "Catering available"],
      phone=None, addr="Rosemary District, Sarasota, FL"),
    B(name="SRQ Handyman Services", theme="steel", emoji="🛠️", cat="Handyman & Remodeling",
      tagline="SRQ Magazine's Best Fence Installer & Best Bathroom Remodeler, 2025.",
      about="Owner-operated since 2018 by Alexander Herbert, SRQ Handyman Services was voted Best Fence Installer and Best Bathroom Remodeler by SRQ Magazine readers in 2025. Quality work, straight answers.",
      services=["Bathroom remodeling", "Fence installation", "General handyman work", "Home improvement projects"],
      badges=["SRQ Magazine winner 2025", "Owner-operated", "Serving Sarasota since 2018"],
      phone=None, addr="Sarasota, FL"),
    B(name="Derek's Handyman Service", theme="steel", emoji="🧰", cat="Handyman Services",
      tagline="Honest, affordable handyman work in Sarasota.",
      about="From small fixes to weekend-project rescues, Derek's Handyman Service gets it done without the runaround. Local, reliable, and easy to reach.",
      services=["General repairs", "Assembly & installs", "Odd jobs & punch lists", "Free estimates"],
      badges=["Local & owner-operated", "Free estimates", "Easy scheduling"],
      phone="(941) 405-2821", addr="Sarasota, FL"),
    # --- Home services ---
    B(name="GL Grasslands Lawn Care & Landscaping", theme="fresh", emoji="🌿", cat="Lawn Care & Landscaping",
      tagline="Full-service lawn care, English y Español.",
      about="GL Grasslands keeps Sarasota yards sharp year-round — mowing, edging, cleanups, and landscaping from a hardworking bilingual crew.",
      services=["Mowing & edging", "Landscaping", "Yard cleanups", "Mulch & planting"],
      badges=["Bilingual crew", "Licensed Florida LLC", "Serving all of Sarasota"],
      phone=None, addr="Sarasota, FL"),
    B(name="Lighthouse Lawn Care FL", theme="fresh", emoji="🌱", cat="Lawn Care",
      tagline="Veteran-owned lawn care you can count on.",
      about="Lighthouse Lawn Care is a veteran-owned Sarasota company delivering dependable mowing and lawn maintenance with military attention to detail.",
      services=["Weekly & biweekly mowing", "Edging & trimming", "Cleanups", "Maintenance plans"],
      badges=["Veteran-owned", "Chamber-listed", "Reliable scheduling"],
      phone="(941) 323-6020", addr="Sarasota, FL"),
    B(name="Boss Lady Pressure Cleaning", theme="fresh", emoji="💦", cat="Pressure Washing",
      tagline="Woman-owned. Neighborhood Favorite. Spotless results.",
      about="With 12 years of experience, Boss Lady Pressure Cleaning earned Nextdoor's Neighborhood Favorite award in both 2023 and 2024. Driveways, roofs, pool decks — we make it look new again.",
      services=["House washing", "Driveways & sidewalks", "Roof cleaning", "Pool decks & lanais"],
      badges=["Woman-owned", "Nextdoor Favorite 2023 & 2024", "12 years experience"],
      phone="(239) 898-2283", addr="Sarasota, FL"),
    B(name="Southwest Florida Painting and Handyman Services", theme="steel", emoji="🎨", cat="Painting & Handyman",
      tagline="First-responder owned. Precision painting and repairs.",
      about="Owned and operated by a first responder, SWFL Painting and Handyman Services brings discipline and care to interior and exterior painting plus general handyman work across Sarasota County.",
      services=["Interior painting", "Exterior painting", "Drywall & repairs", "Handyman projects"],
      badges=["First-responder owned", "Interior & exterior", "Sarasota County wide"],
      phone=None, addr="Sarasota County, FL"),
    B(name="OCD Cleaning of Sarasota", theme="fresh", emoji="🧽", cat="Cleaning Services",
      tagline="Obsessively clean homes and offices.",
      about="OCD Cleaning of Sarasota has been making homes and offices spotless since 2020. Detail-obsessed, dependable, and local.",
      services=["Home cleaning", "Office cleaning", "Deep cleans", "Recurring service"],
      badges=["Homes & offices", "Detail-obsessed", "Active Florida LLC"],
      phone="(941) 301-7937", addr="200 Honore Ave, Sarasota, FL 34232"),
    B(name="Sarasota Pooligans", theme="ocean", emoji="🏊", cat="Pool Service",
      tagline="Weekly pool cleaning without the hassle.",
      about="Sarasota Pooligans is a locally owned pool service offering weekly cleaning, free quotes, and honest work — Monday through Saturday, 7 to 7.",
      services=["Weekly pool cleaning", "Chemical balancing", "Filter maintenance", "Free quotes"],
      badges=["Locally owned", "Mon–Sat 7am–7pm", "Free quotes"],
      phone="(941) 298-4042", addr="Sarasota, FL 34231"),
    B(name="Sarasota Pool Cleaning And Repair", theme="ocean", emoji="🔧", cat="Pool Cleaning & Repair",
      tagline="Cleaning and repairs for Sarasota pools.",
      about="Pool cleaning and repair for Sarasota homeowners — maintenance visits, equipment fixes, and green-to-clean rescues.",
      services=["Pool cleaning", "Equipment repair", "Green-to-clean", "Maintenance plans"],
      badges=["Cleaning + repair", "Local operator", "Responsive service"],
      phone=None, addr="Sarasota, FL"),
    B(name="EC Service & Moving", theme="steel", emoji="📦", cat="Moving Services",
      tagline="Five-star local moving — pianos and pool tables included.",
      about="EC Service & Moving handles local moves of every kind, including the hard stuff: pianos, office moves, and pool tables. Five-star rated by customers.",
      services=["Local moving", "Piano moving", "Office relocation", "Pool table moving"],
      badges=["5-star rated", "Specialty items", "Sarasota local"],
      phone=None, addr="Sarasota, FL"),
    B(name="Martinez Drywall & Remodeling", theme="steel", emoji="🧱", cat="Drywall & Remodeling",
      tagline="Clean drywall work, fast responses, free estimates.",
      about="Martinez Drywall & Remodeling delivers quality drywall installation, repair, and remodeling across Sarasota — with fast responses and free estimates.",
      services=["Drywall installation", "Drywall repair & texture", "Remodeling", "Free estimates"],
      badges=["Free estimates", "Fast response", "Registered Florida LLC"],
      phone=None, addr="4523 Olive Ave, Sarasota, FL 34231"),
    # --- Food & drink ---
    B(name="Croz's Surfshack", theme="fiesta", emoji="🌭", cat="Food Truck — Gourmet Hot Dogs & Hawaiian",
      tagline="Gourmet dogs and island flavor since 2014.",
      about="Croz's Surfshack has been rolling through Sarasota and Bradenton since 2014 with gourmet hot dogs and Hawaiian-style plates. Catch the truck — follow us for locations and specials.",
      services=["Gourmet hot dogs", "Hawaiian plates", "Events & catering", "Location updates on socials"],
      badges=["Est. 2014", "Sarasota & Bradenton", "Event catering"],
      phone="(941) 586-3023", addr="Mobile — Sarasota/Bradenton, FL"),
    B(name="Lady Lola Food Truck", theme="fiesta", emoji="🫓", cat="Venezuelan Food Truck",
      tagline="Empanadas, pepitos, and Venezuelan street food hecho con amor.",
      about="Lady Lola serves authentic Venezuelan street food — crispy empanadas, loaded pepitos, and more. Order online or find the truck on S Tamiami Trail.",
      services=["Empanadas", "Pepitos & arepas", "Online ordering", "Catering"],
      badges=["Authentic Venezuelan", "Online ordering", "Local favorite"],
      phone="(941) 667-1005", addr="6104 S Tamiami Trl, Sarasota, FL"),
    B(name="Dan Apizz' Man — New Haven Style", theme="fiesta", emoji="🍕", cat="Wood-Fired Pizza Truck",
      tagline="Real New Haven apizza, wood-fired in Sarasota.",
      about="Dan Apizz' Man brings true New Haven-style apizza to Sarasota — charred, thin, and wood-fired. Saturdays at the Sarasota Farmers Market, Wednesday through Friday at Sun King Brewery.",
      services=["Wood-fired New Haven pizza", "Sat @ Sarasota Farmers Market", "Wed–Fri @ Sun King Brewery", "Private events"],
      badges=["New Haven style", "53 rave reviews", "Farmers Market regular"],
      phone="(516) 476-0699", addr="1215 Mango Ave, Sarasota, FL 34237"),
    B(name="Caribbean BBQ Truck", theme="fiesta", emoji="🔥", cat="Caribbean BBQ & Jerk",
      tagline="Slow smoke. Island spice. Wednesday–Saturday.",
      about="Real Caribbean BBQ and jerk, smoked slow and seasoned right. Find us at 3250 Desoto Rd Wednesday through Saturday, or order on Uber Eats.",
      services=["Jerk chicken", "Caribbean BBQ plates", "Uber Eats delivery", "Open Wed–Sat"],
      badges=["Wed–Sat", "On Uber Eats", "Authentic jerk"],
      phone="(941) 879-7144", addr="3250 Desoto Rd, Sarasota, FL"),
    B(name="La Cajita SRQ Food Truck", theme="fiesta", emoji="🥘", cat="Mexican-Cuban Fusion Truck",
      tagline="Mexican-Cuban fusion, Saturdays at Sun King Brewery.",
      about="La Cajita SRQ blends Mexican and Cuban flavors into one unforgettable menu. Catch us Saturdays at Sun King Brewery or book us for your next event.",
      services=["Mexican-Cuban fusion menu", "Saturdays @ Sun King Brewery", "Event catering", "Delivery on Uber Eats"],
      badges=["Fusion menu", "Event catering", "On Uber Eats"],
      phone=None, addr="Sarasota, FL — Saturdays @ Sun King Brewery"),
    B(name="Gran Arepa Southwest", theme="fiesta", emoji="🌽", cat="Colombian Food Truck",
      tagline="Colombian arepas and empanadas, made fresh in SW Florida.",
      about="Gran Arepa Southwest brings handmade Colombian arepas and empanadas to Sarasota and Southwest Florida. Follow us on Instagram for locations.",
      services=["Arepas", "Empanadas", "Colombian street food", "Events"],
      badges=["Handmade daily", "Sarasota/SW FL", "Follow on Instagram"],
      phone=None, addr="Mobile — Sarasota/SW Florida"),
    # --- Personal care & pets ---
    B(name="Phatheadz Barbershop", theme="barber", emoji="✂️", cat="Barbershop",
      tagline="Serving Newtown since 2008. Book online in seconds.",
      about="Phatheadz Barbershop has served the Newtown community since 2008. Minority-owned, Chamber member, and easy to book — fades, tapers, designs, and more.",
      services=["Fades & tapers", "Designs & lineups", "Beard work", "Online booking"],
      badges=["Since 2008", "Minority-owned", "Chamber member"],
      phone="(941) 917-0329", addr="1818 Dr Martin Luther King Jr Way, Sarasota, FL 34234"),
    B(name="5STAR Barbershop", theme="barber", emoji="⭐", cat="Barbershop",
      tagline="4.9 stars. The name says it all.",
      about="5STAR Barbershop lives up to the name — 4.9 stars across dozens of reviews. Book online and get a cut that earns its rating.",
      services=["Cuts & fades", "Beard trims", "Kids' cuts", "Online booking"],
      badges=["4.9★ rating", "Online booking", "Sarasota local"],
      phone=None, addr="3050 17th St, Sarasota, FL 34234"),
    B(name="Pat's Barbershop", theme="barber", emoji="💈", cat="Barbershop",
      tagline="Old-fashioned barbershop with modern flair.",
      about="Pat's Barbershop blends old-school barbering tradition with modern style. Classic cuts, hot lather, and conversation worth the chair time.",
      services=["Classic cuts", "Modern styles", "Beard & shave service", "Appointments & walk-ins"],
      badges=["Old-school tradition", "Modern styles", "Neighborhood staple"],
      phone="(941) 365-5441", addr="935 N Beneva Rd Ste 615, Sarasota, FL"),
    B(name="Cattlemen Barber Shop", theme="barber", emoji="🤠", cat="Barbershop",
      tagline="Four chairs, no fuss. Walk-ins welcome since 2009.",
      about="Cattlemen Barber Shop is a four-chair, walk-in-friendly shop that's been cutting Sarasota's hair since 2009. Licensed, quick, and consistent.",
      services=["Men's cuts", "Flat tops & fades", "Seniors & kids", "Walk-ins welcome"],
      badges=["Est. 2009", "Walk-ins welcome", "FL licensed"],
      phone="(941) 377-6611", addr="999 Cattlemen Rd Unit D, Sarasota, FL 34232"),
    B(name="Gulf Gate Barbershop", theme="barber", emoji="🌴", cat="Barbershop",
      tagline="Your neighborhood barbershop in Gulf Gate.",
      about="Gulf Gate Barbershop keeps the neighborhood looking sharp — quality cuts in the heart of Gulf Gate, without the wait or the price tag.",
      services=["Haircuts", "Fades & tapers", "Beard trims", "Booking via Fresha"],
      badges=["Gulf Gate local", "Book on Fresha", "Neighborhood prices"],
      phone=None, addr="6575 Gateway Ave, Sarasota, FL 34231"),
    B(name="Family Hair Salon & Barber Shop", theme="blush", emoji="👨‍👩‍👧", cat="Family Salon & Barbershop",
      tagline="Cuts, color, and nails for the whole family.",
      about="One stop for the whole family — men's and women's cuts, kids' cuts, color, and nails. Freshly remodeled under new ownership on Bee Ridge Road.",
      services=["Kids' cuts", "Men's & women's cuts", "Color", "Nails"],
      badges=["Whole-family services", "Newly remodeled", "Bee Ridge Rd"],
      phone=None, addr="4517 Bee Ridge Rd, Sarasota, FL 34233"),
    B(name="TT Nails Spa", theme="blush", emoji="💅", cat="Nail Salon",
      tagline="Walk-ins welcome. Women-owned. Beautifully done.",
      about="TT Nails Spa is a women-owned salon where walk-ins are always welcome. Manicures, pedicures, and nail art done with care.",
      services=["Manicures", "Pedicures", "Gel & dip", "Nail art"],
      badges=["Women-owned", "Walk-ins welcome", "Lockwood Ridge"],
      phone="(941) 359-1117", addr="6370 N Lockwood Ridge Rd, Sarasota, FL 34243"),
    B(name="Pink Petals Nail Spa", theme="blush", emoji="🌸", cat="Nail Salon",
      tagline="4.9 stars across 687 reviews — and counting.",
      about="Pink Petals Nail Spa has earned 4.9 stars across nearly 700 reviews. Impeccable manicures, relaxing pedicures, and a spotless studio near University Parkway.",
      services=["Manicures & pedicures", "Gel, dip & acrylic", "Spa treatments", "Group bookings"],
      badges=["4.9★ / 687 reviews", "University Pkwy", "Book on Fresha"],
      phone="(941) 358-3851", addr="3315 University Pkwy #102, Sarasota, FL 34243"),
    B(name="Valentine's Nail Spa", theme="blush", emoji="💖", cat="Nail Salon",
      tagline="The busy little nail spa on the South Trail.",
      about="Valentine's Nail Spa is a South Tamiami Trail favorite — busy for a reason. Quality sets, friendly techs, fair prices.",
      services=["Full sets", "Manicures & pedicures", "Gel & designs", "Waxing"],
      badges=["79+ reviews", "South Trail", "Fair prices"],
      phone="(941) 922-8282", addr="7350 S Tamiami Trl, Sarasota, FL 34231"),
    B(name="Kelly's Private Home Dog Grooming", theme="paws", emoji="🐩", cat="Dog Grooming",
      tagline="Calm, private, one-on-one grooming for small dogs.",
      about="15 years of grooming experience in a calm, private home setting — no cages, no chaos. Specializing in small dogs, by appointment.",
      services=["Small-dog grooming", "Bath & tidy", "Private one-on-one setting", "By appointment"],
      badges=["15 years experience", "Private home studio", "Small-dog specialist"],
      phone="(941) 284-4083", addr="Bahia Vista area, Sarasota, FL"),
    B(name="Shaggy Companions", theme="paws", emoji="🐕", cat="Pet Sitting & Dog Walking",
      tagline="Tailored in-home pet care while you're away.",
      about="Shaggy Companions provides personalized in-home pet sitting and dog walking across Sarasota — your pets keep their routine, you keep your peace of mind.",
      services=["In-home pet sitting", "Dog walking", "Vacation visits", "Custom care plans"],
      badges=["In-home care", "Custom plans", "Sarasota local"],
      phone=None, addr="Sarasota, FL"),
    B(name="Lesley's Pet Sitters", theme="paws", emoji="🐾", cat="Pet Sitting & Dog Walking",
      tagline="Top-12 rated pet care for Sarasota, Bradenton & Venice.",
      about="Lesley's Pet Sitters offers in-home care, walks, and medication visits with a 100% recommendation rate — rated among the area's top 12 pet sitters.",
      services=["In-home pet sitting", "Dog walking", "Medication visits", "Serving Sarasota, Bradenton & Venice"],
      badges=["100% recommended", "Top-12 area rating", "Meds experience"],
      phone="(941) 228-3209", addr="33 S Gulfstream Ave, Sarasota, FL 34236"),
    B(name="Rare Auto Detailing", theme="steel", emoji="🚗", cat="Mobile Auto Detailing",
      tagline="Certified ceramic coating and tint — we come to you.",
      about="Rare Auto Detailing is IGL Ceramic and MAXPRO Tint certified, bringing showroom-level detailing, coatings, and tint straight to your driveway.",
      services=["Full detailing", "IGL ceramic coating", "MAXPRO window tint", "Mobile — we come to you"],
      badges=["IGL certified", "MAXPRO certified", "100% recommended"],
      phone="(941) 914-8102", addr="Mobile — Sarasota, FL"),
    # --- Retail & trades ---
    B(name="American Pie Antiques & Collectibles", theme="vintage", emoji="🏺", cat="Antiques & Collectibles",
      tagline="Downtown Sarasota's treasure chest on Fruitville Road.",
      about="American Pie Antiques & Collectibles is packed with finds — vintage Americana, collectibles, and one-of-a-kind pieces in downtown Sarasota.",
      services=["Antiques & vintage", "Collectibles", "Americana", "New finds weekly"],
      badges=["Downtown Sarasota", "One-of-a-kind finds", "Browse-worthy"],
      phone="(941) 362-0682", addr="1470 Fruitville Rd, Sarasota, FL 34236"),
    B(name="Suncoast Auto Repair of Sarasota", theme="steel", emoji="🔩", cat="Auto Repair",
      tagline="Honest auto repair on 17th Street.",
      about="Suncoast Auto Repair of Sarasota is an independent, BBB-listed shop doing honest diagnostic and repair work — the neighborhood alternative to dealership prices.",
      services=["Diagnostics", "Brakes & suspension", "Engine & transmission", "Scheduled maintenance"],
      badges=["Independent shop", "BBB listed", "Active FL LLC"],
      phone="(941) 954-6097", addr="2221 17th St, Sarasota, FL 34234"),
    B(name="The Bike Shop", theme="fresh", emoji="🚲", cat="Bicycle Sales & Repair",
      tagline="Sales, service, and straight answers on McIntosh Road.",
      about="The Bike Shop keeps Sarasota riding — tune-ups, repairs, and bikes without the big-box attitude.",
      services=["Tune-ups", "Repairs", "Bike sales", "Parts & accessories"],
      badges=["Local shop", "McIntosh Rd", "Service first"],
      phone="(941) 404-9090", addr="5444 McIntosh Rd, Sarasota, FL 34232"),
    B(name="Sooper Dooper Bikes", theme="fresh", emoji="🚴", cat="Mobile Bike Repair",
      tagline="20+ years of bike repair — delivered to your door.",
      about="Sooper Dooper Bikes brings 20+ years of repair experience to you, with regular stops across Sarasota and Manatee counties — Longboat Key, West Bradenton, and more. Call or text.",
      services=["Mobile bike repair", "Tune-ups at your door", "Regular neighborhood stops", "Call or text to book"],
      badges=["20+ years experience", "Mobile service", "Sarasota & Manatee"],
      phone="(941) 289-7861", addr="Mobile — Sarasota & Manatee counties"),
    B(name="Manasota Mobile Marine", theme="ocean", emoji="🛠️", cat="Mobile Boat & Outboard Repair",
      tagline="Certified outboard repair that comes to your dock.",
      about="Manasota Mobile Marine is a certified outboard specialist serving Sarasota and Manatee counties — repairs and maintenance at your dock, lift, or driveway.",
      services=["Outboard repair", "Dockside service", "Maintenance & winterizing", "Sarasota & Manatee counties"],
      badges=["Certified outboard specialist", "We come to you", "Two-county coverage"],
      phone="(941) 745-1444", addr="Mobile — Sarasota & Manatee counties"),
]

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{name} — {cat} | Sarasota, FL (Concept Demo)</title>
<style>
:root {{ --bg:{bg}; --surface:{surface}; --ink:{ink}; --accent:{accent}; --accent2:{accent2}; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; background:var(--bg); color:var(--ink); line-height:1.6; }}
.demo-banner {{ background:#111; color:#fff; text-align:center; font-size:.78rem; padding:.45rem .75rem; letter-spacing:.02em; }}
.demo-banner strong {{ color:#fbbf24; }}
header {{ background:{hero}; color:#fff; padding:4.5rem 1.25rem 5rem; text-align:center; }}
.mark {{ font-size:3.2rem; line-height:1; display:inline-block; background:rgba(255,255,255,.14); border-radius:24px; padding:.9rem 1.1rem; margin-bottom:1.2rem; }}
header h1 {{ font-size:clamp(1.9rem,5vw,3rem); letter-spacing:-.02em; margin-bottom:.4rem; }}
header .cat {{ text-transform:uppercase; letter-spacing:.18em; font-size:.8rem; opacity:.85; margin-bottom:1rem; }}
header p.tag {{ font-size:clamp(1.05rem,2.5vw,1.3rem); max-width:34rem; margin:0 auto 1.8rem; opacity:.95; }}
.cta {{ display:inline-block; background:#fff; color:var(--ink); font-weight:700; padding:.85rem 1.9rem; border-radius:999px; text-decoration:none; font-size:1.05rem; box-shadow:0 6px 18px rgba(0,0,0,.25); }}
.badges {{ display:flex; flex-wrap:wrap; gap:.6rem; justify-content:center; margin-top:2rem; }}
.badge {{ background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.35); border-radius:999px; padding:.35rem .95rem; font-size:.85rem; }}
main {{ max-width:60rem; margin:-2.5rem auto 0; padding:0 1.25rem 3rem; }}
section.card {{ background:var(--surface); border-radius:18px; padding:2rem; margin-bottom:1.5rem; box-shadow:0 10px 30px rgba(0,0,0,.07); }}
h2 {{ font-size:1.35rem; margin-bottom:.9rem; }}
h2::after {{ content:""; display:block; width:3rem; height:4px; border-radius:2px; background:var(--accent2); margin-top:.45rem; }}
.services {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(13rem,1fr)); gap:.9rem; margin-top:1.1rem; }}
.svc {{ background:var(--bg); border-radius:12px; padding:1rem 1.1rem; font-weight:600; display:flex; align-items:center; gap:.6rem; }}
.svc::before {{ content:"✓"; color:var(--accent); font-weight:800; }}
.contact-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(14rem,1fr)); gap:1rem; margin-top:1rem; }}
.contact-item {{ background:var(--bg); border-radius:12px; padding:1.1rem 1.2rem; }}
.contact-item .label {{ text-transform:uppercase; font-size:.72rem; letter-spacing:.14em; opacity:.65; margin-bottom:.25rem; }}
.contact-item a {{ color:var(--accent); font-weight:700; text-decoration:none; font-size:1.1rem; }}
footer {{ text-align:center; font-size:.8rem; padding:2rem 1.25rem 3rem; opacity:.7; max-width:44rem; margin:0 auto; }}
@media (max-width:600px) {{ header {{ padding:3rem 1rem 4rem; }} section.card {{ padding:1.4rem; }} }}
</style>
</head>
<body>
<div class="demo-banner"><strong>CONCEPT DEMO</strong> — design mockup prepared as a proposal. Not the official website of {name}.</div>
<header>
  <span class="mark">{emoji}</span>
  <div class="cat">{cat} · Sarasota, FL</div>
  <h1>{name}</h1>
  <p class="tag">{tagline}</p>
  {cta}
  <div class="badges">{badges}</div>
</header>
<main>
  <section class="card"><h2>About</h2><p>{about}</p></section>
  <section class="card"><h2>What We Do</h2><div class="services">{services}</div></section>
  <section class="card"><h2>Visit or Call</h2>
    <div class="contact-grid">
      <div class="contact-item"><div class="label">Location</div><div>{addr}</div></div>
      {phone_block}
    </div>
  </section>
</main>
<footer>Concept website mockup generated for pitch purposes. Business details compiled from public listings and should be verified with the owner before publication. This page is not affiliated with or approved by {name}.</footer>
</body>
</html>
"""

def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)

def build():
    cards = []
    for b in BUSINESSES:
        slug = slugify(b["name"])
        theme = THEMES[b["theme"]]
        e = html.escape
        phone = b.get("phone")
        tel = re.sub(r"\D", "", phone) if phone else ""
        cta = f'<a class="cta" href="tel:{tel}">📞 Call {e(phone)}</a>' if phone else '<a class="cta" href="#contact">Get in touch</a>'
        phone_block = (f'<div class="contact-item"><div class="label">Phone</div>'
                       f'<a href="tel:{tel}">{e(phone)}</a></div>') if phone else \
                      '<div class="contact-item"><div class="label">Contact</div><div>Reach out via our social pages</div></div>'
        page = PAGE.format(
            name=e(b["name"]), cat=e(b["cat"]), tagline=e(b["tagline"]), about=e(b["about"]),
            emoji=b["emoji"], addr=e(b["addr"]), cta=cta, phone_block=phone_block,
            badges="".join(f'<span class="badge">{e(x)}</span>' for x in b["badges"]),
            services="".join(f'<div class="svc">{e(s)}</div>' for s in b["services"]),
            bg=theme[0], surface=theme[1], ink=theme[2], accent=theme[3], accent2=theme[4], hero=theme[5],
        )
        d = os.path.join(ROOT, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(page)
        cards.append((slug, b))

    # gallery
    items = "".join(
        f'<a class="tile" href="{slug}/index.html" style="--g:{THEMES[b["theme"]][5]}">'
        f'<div class="hero">{b["emoji"]}</div>'
        f'<div class="body"><h3>{html.escape(b["name"])}</h3>'
        f'<p>{html.escape(b["cat"])}</p></div></a>'
        for slug, b in cards)
    gallery = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Sarasota Demo Sites — Gallery ({len(cards)} concepts)</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; background:#f3f4f6; color:#111827; padding:2rem 1.25rem 4rem; }}
h1 {{ text-align:center; margin-bottom:.4rem; }}
p.sub {{ text-align:center; opacity:.7; margin-bottom:2.2rem; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(15rem,1fr)); gap:1.1rem; max-width:72rem; margin:0 auto; }}
.tile {{ background:#fff; border-radius:14px; overflow:hidden; text-decoration:none; color:inherit; box-shadow:0 4px 14px rgba(0,0,0,.08); transition:transform .12s; }}
.tile:hover {{ transform:translateY(-3px); }}
.tile .hero {{ background:var(--g); font-size:2.6rem; text-align:center; padding:1.6rem 0; }}
.tile .body {{ padding: .9rem 1rem 1.1rem; }}
.tile h3 {{ font-size:1rem; margin-bottom:.15rem; }}
.tile p {{ font-size:.8rem; opacity:.65; }}
</style></head><body>
<h1>Sarasota Concept Demo Sites</h1>
<p class="sub">{len(cards)} pitch-ready one-page website concepts — click any tile to preview</p>
<div class="grid">{items}</div>
</body></html>"""
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(gallery)
    print(f"Built {len(cards)} demo sites + gallery")

if __name__ == "__main__":
    build()
