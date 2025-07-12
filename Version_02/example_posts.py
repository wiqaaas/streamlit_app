import json

# ─── Your example posts ───────────────────────────────────────────
posts = [
  {
    "Platform": "Facebook",
    "Topic /  Category": "National Association News",
    "Content": "Our friends of the Uzbekistan Polo Federation has their first ever General Assembly on October 10th, 2020."
  },
  {
    "Platform": "Facebook",
    "Topic /  Category": "Quote",
    "Content": "Great sportsmanship during games is the key ingredient to long lasting friendships. #InternationalDayOfPeace #USPoloAssn #LiveAuthentically"
  },
  {
    "Platform": "Facebook",
    "Topic /  Category": "Motivation post",
    "Content": "#MotivationMonday Virginia 🔜 Florida 🙌 Polo ponies are beginning to head south for the season including those of 🔟-goaler Polito pieres and we can hardly wait! Check out this awesome drone footage from Marcos Bignoli!"
  },
  {
    "Platform": "Facebook",
    "Topic /  Category": "Event Announcements",
    "Content": "The King Power Gold Cup for the British Open Polo Championship opens on Wednesday 1st July at Cowdray Park."
  },
  {
    "Platform": "Instagram",
    "Topic /  Category": "Sponsors mentions",
    "Content": "Strength and resilience on and off the polo field with @HopeArellano! @USPoloAssn #GirlsTakeover #InternationalDayofTheGirl #USPoloAssn #USPAinspire"
  },
  {
    "Platform": "Instagram",
    "Topic /  Category": "Team News",
    "Content": "Team @USPoloAssn is ready to practice! #USPoloAssn #LiveAuthentically"
  },
  {
    "Platform": "Instagram",
    "Topic /  Category": "throwback post",
    "Content": "Mondays are great for a trip down memory lane! 2002 #equipedefrance #polo #italie @roma_polo_club"
  },
  {
    "Platform": "Instagram",
    "Topic /  Category": "Video highlight",
    "Content": "Relive the North American Cup® Final action! 💥💪 Most Valuable Player @nicroldan showing off his impressive 8️⃣-goal skills for @casablancapolo! 🤩"
  },
  {
    "Platform": "Instagram",
    "Topic /  Category": "News Item",
    "Content": "Enjoy up to an incredible 70% off in the Hurlingham Polo Outlet Store this Cyber Weekend. Available until midnight on Monday 30th November 2020, including free UK delivery."
  },
  {
    "Platform": "Instagram",
    "Topic /  Category": "Quote",
    "Content": "Today we salute the men and women who fought for our freedom and contribute so much to our sport! 🇺🇸#HappyVeteransDay #repost @ocpoloclub #poloattheranch"
  },
  {
    "Platform": "Twitter",
    "Topic /  Category": "News Item",
    "Content": "Check out our new FIP Magazine! https://fippolo.com/newsletter/fip-magazine-1-august-2019/"
  },
  {
    "Platform": "Twitter",
    "Topic /  Category": "Partner colaboration post",
    "Content": "Regent's Uni London @regentsuni · 16 abr. 2018 Regent's are delighted to have formed a scholarship agreement with @PoloDevelopment 🐴. Apply now 👉 https://bit.ly/2EQ8tyi #MondayMotivation"
  },
  {
    "Platform": "Twitter",
    "Topic /  Category": "Motivation Post",
    "Content": "Great Polo players are not great because of their technique, they are great because of their passion. #MondayMotivation"
  },
  {
    "Platform": "Twitter",
    "Topic /  Category": "Video highlight",
    "Content": "Congrats Valiente!! Winners 8-6 in the Ylvisaker Cup! Levantando las manos #USPALive"
  },
  {
    "Platform": "Twitter",
    "Topic /  Category": "Game report",
    "Content": "US Polo Association @PoloAssociation · 4 mar. 2018 Congrats to Valiente!! Winners of the 2018 C.V. Whitney Cup 9-4 over Colorado TrofeoTrofeo #USPALive"
  },
  {
    "Platform": "Twitter",
    "Topic /  Category": "Member interaction post",
    "Content": "All the cool people are doing it 😉#drop_your_beautiful_horse_head_challenge"
  },
  {
    "Platform": "Article on website",
    "Topic /  Category": "Game Articles",
    "Content": "Climbing from behind, Aspen Snowmass reach the pinnacle of success and take their place as 2020 U.S. Open Women's Handicap champions! 🏔👏👏 Photos and full recap on the action below! 💪⬇️"
  },
  {
    "Platform": "Article on website",
    "Topic /  Category": "Partner colaboration post",
    "Content": "SHOP AND SCORE FOR YOUR I/I CLUB WITH TICO’S WHOOPIES"
  },
  {
    "Platform": "Linkedin",
    "Topic /  Category": "About info",
    "Content": "Founded in 1890, the United States Polo Association (USPA) is the national governing body for the sport of polo in North America and is the second oldest sport governing body in the United States..."
  },
  {
    "Platform": "Facebook",
    "Topic /  Category": "Game Report",
    "Content": "Competing against a beautiful fall backdrop at Westchester Polo Club, The Avery not only claimed the coveted Northeastern Circuit Arena Women's Challenge Cup but also cashed in with $1,500 in tournament prize money! 🍁👏"
  }
]

# JSON-serialize once
example_posts_json = json.dumps(posts, ensure_ascii=False)
