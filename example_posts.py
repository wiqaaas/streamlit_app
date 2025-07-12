import json

# ─── Your example posts ───────────────────────────────────────────
posts = [
  {
    "Platform": "Instagram",
    "Category": "Match Promotion",
    "Content": "🔥 Saddle up for July 7 when La Dolfina/Marques de Riscal charges into battle against Park Place at Cowdray Park! Remember last year’s heart-stopping overtime where Park Place snatched victory from the jaws of defeat? 😱 While counting down the days, unlock pro secrets in 'Player Insight - Diego Cavanagh' and ride into the game like a champion! 🏇✨"
  },
  {
    "Platform": "Twitter",
    "Category": "Highlight Recap",
    "Content": "⏳ The clock’s ticking for July 8: Scone Polo vs UAE Polo! Sparks flew last season when UAE Polo staged a jaw-dropping comeback that left fans breathless. 💥 Want to master those clutch plays yourself? Hit up 'Passing - Offside Forehand' in our eLearning hub and sharpen your game! 🚀📚"
  },
  {
    "Platform": "Facebook",
    "Category": "Fan Engagement",
    "Content": "🌟 Get hyped for July 9 as Dubai Polo faces Monterosso in a duel set to shake Cowdray Park! Who could forget Monterosso’s underdog triumph that sent shockwaves through the stands last year? 🙌 If you’re hungry to know how underdogs turn legends, dive into 'Defensive Tactics in High-Goal Polo' and discover the secrets of champions. 🎯🏆"
  }
]

# JSON-serialize once
example_posts_json = json.dumps(posts, ensure_ascii=False)
