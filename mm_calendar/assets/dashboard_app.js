const MONTHS = __MONTHS__;
const VARIANT_DATES = __VARIANT_DATES__;
const WEEKDAYS = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
const MONTH_LABEL = {"2026-04":"April 2026","2026-05":"May 2026","2026-06":"June 2026","2026-07":"July 2026","2026-08":"August 2026"};
const MONTH_KEYS = ["2026-04","2026-05","2026-06","2026-07","2026-08"];
let currentMonthKey = MONTH_KEYS.includes("2026-08") ? "2026-08" : (MONTH_KEYS.includes("2026-07") ? "2026-07" : MONTH_KEYS[0]);
const CAL_BASELINE = JSON.parse(JSON.stringify(MONTHS));
const CAL_EDIT_PREFIX = "mm_cal_edits_v1_";
const CAL_ITEM_STATUSES = ["Daily deal","Offers & coin sale","Rolling offer","Buy all","RYD","Counter PO","Prize Mania","MGAP","Gems","Core","Clan-Dash","ADS","Black Diamond"];
const CAL_PRICING_OPTIONS = ["","Medium","High","Max"];
const MONTH_OPEN_DENOM_DRIVER={
  id:"month_open_biggest_denom",
  label:"1st of month — biggest store denom",
  kind:"purchase_driver",
  monday_product:"Offers & coin sale",
  desc:"Added to the store denom,\ngives both coins & gems like the american denom in 4th of july"
};
const CAT_COLOR = {dd:"#22c55e",offers:"#4f9cff",mgap:"#ec4899",gems:"#eab308",core:"#f97316",features:"#22d3ee",gameplay:"#a855f7",ads:"#94a3b8",anchor:"#f59e0b"};
const CAT_LABEL = {dd:"Daily Deal",offers:"Offers (Buy All/Rolling/RYD/Coin Sale)",mgap:"MGAP",gems:"Gems / boosters",core:"Core / gameplay challenge",features:"Piggy · Lotto · LBP · Dice",gameplay:"Shiny Show / Clan / Album / Machine",ads:"ADS",anchor:"Anchor / event / album"};
const SEASON_COLOR = {"Short Term":"#f59e0b","Mid Term":"#06b6d4","Album":"#a855f7"};
const SEASON_ABBR = {"Short Term":"Short","Mid Term":"Mid","Album":"Album"};

function classify(text){
  const s=(text||"").toLowerCase();
  if(s.startsWith("dd")||s.startsWith("daily deal"))return"dd";
  if(s.startsWith("ads"))return"ads";
  if(s.includes("mgap"))return"mgap";
  if(s.includes("gemback")||s.includes("ggs")||s.startsWith("gems")||s.includes("gem "))return"gems";
  if(s.includes("buy all")||s.includes("bonanza")||s.includes("decoy")||s.includes("rolling")||s.startsWith("ryd")||/coins? sale/.test(s)||s.includes("counter po")||s.includes("limited po")||s.includes("prize mania")||s.includes("scratch")||s.includes("sb ")||s.includes("700% sb")||s.includes("golden spin")||s.includes("mystery buy all")||/\blbp\s*[—-]/.test(s)||(/lotto/.test(s)&&/peak/.test(s)))return"offers";
  // Core / coin-sink challenges — orange, separate from general gameplay
  if(s.includes("ace loot")||s.includes("spin zone")||s.includes("win master")||s.includes("ace heist")||s.includes("pyp")||s.includes("spinner clash")||s.includes("custom pod")||/\bmes\b/.test(s)||s.includes("puzzle m.e.s")||s.includes("betty")||s.includes("status boost"))return"core";
  if(s.includes("piggy"))return"offers";
  if(s.includes("dice booster")||s.includes("dice deluxe"))return"features";
  if(s.includes("core")||s.includes("shiny show")||s.includes("clan")||s.includes("dash")||(/loot/.test(s)&&!s.includes("ace loot"))||s.includes("machine")||s.includes("growing shiny")||s.includes("sneak peek")||s.includes("shiny wolf")||s.includes("hoppin"))return"gameplay";
  return"anchor";
}
// ---- Offer content explainer ----
// Real board item names range from fully spelled-out ("Buy All - 2 GGS + 4 RDS + Lotto
// Bonus + Dice Booster 8 hrs + 3 Hammers | H Pricing") to terse ("Rolling Offer- 6 cycles").
// The old version of this guessed specific SKUs/amounts from generic keyword patterns —
// for real data that meant presenting made-up numbers as if they were the actual offer
// content. This version instead: (1) shows exactly what the real item name/description say,
// parsed into readable parts — never invented, and (2) explains the offer TYPE's fixed platform
// structure from offer_construction.md, clearly separated as "how this works in general",
// not "here's what's in this specific one".
const PRICE_LABEL={max:"Max",high:"High",h:"High",mid:"Mid",m:"Mid",low:"Low",l:"Low"};
function parseOfferParts(rawName){
  let s=String(rawName||"");
  let timeWindow=null, pricingTag=null;
  const timeM=s.match(/\b\d{1,2}:\d{2}(?:-\d{1,2}:\d{2})?\s*(?:UTC)?\b/i);
  if(timeM){timeWindow=timeM[0].trim();s=s.replace(timeM[0],"");}
  const pm=s.match(/\|\s*(Max|High|Mid|Low|H|M|L)\s*(?:Pric(?:e|ing))?\b/i);
  if(pm){pricingTag=pm[1];s=s.replace(pm[0],"");}
  const bm=s.match(/\[(Max|High|Mid|Low|H|M|L)\]/i);
  if(bm){pricingTag=pricingTag||bm[1];s=s.replace(bm[0],"");}
  s=s.replace(/^(Buy All|Decoy(?:\s*\/?\s*Bonanza)?|Bonanza|Rolling Offer|Rolling offer|Rolling|RYD|DD|Daily Deal|Prize Mania|Coins? Sale)\s*[-:–]?\s*/i,"").trim();
  s=s.replace(/^\(\d\)\s*[-:–]?\s*/,"").trim();
  const parts=s.split(/\s*\+\s*|\s*\|\s*|\s*,\s*/).map(function(p){return p.trim();}).filter(Boolean);
  return {parts:parts, pricingTag:pricingTag, timeWindow:timeWindow};
}
const PRIZE_PATTERNS=[
  {group:"Base currency",label:"Coins",rx:/\bcoins?\b/i},
  {group:"Base currency",label:"Gems",rx:/\bgems?\b/i},
  {group:"Stamps / SB",label:"RDS / Red Diamond Stamp",rx:/\bRDS\b|red diamond/i},
  {group:"Stamps / SB",label:"GGS / Gold Gem Stamp",rx:/\bGGS\b|gold gem stamp/i},
  {group:"Stamps / SB",label:"Extreme Stamp",rx:/extreme stamp/i},
  {group:"Stamps / SB",label:"SlotoBucks %",rx:/\b\d{2,4}%\s*SB\b|\bSB\b|slotobucks/i},
  {group:"Gameplay boosters",label:"Hammers",rx:/hammers?/i},
  {group:"Gameplay boosters",label:"Picks",rx:/\bpicks?\b/i},
  {group:"Gameplay boosters",label:"PAB",rx:/\bPAB\b/i},
  {group:"Gameplay boosters",label:"Airstrike / AS",rx:/\bAS\b|air\s*strike/i},
  {group:"Gameplay boosters",label:"Parasheep",rx:/parasheep/i},
  {group:"Gameplay boosters",label:"Superboom",rx:/super\s*boom|superboom/i},
  {group:"Gameplay boosters",label:"Dice Booster / Dice",rx:/dice booster|snl dice|\bdice\b/i},
  {group:"Gameplay boosters",label:"Free Spins",rx:/free spins?/i},
  {group:"Gameplay boosters",label:"Ace Spins",rx:/ace spins?/i},
  {group:"Gameplay boosters",label:"Multiwheel",rx:/multi\s*wheel|multiwheel/i},
  {group:"Gameplay boosters",label:"Shield",rx:/\bshield\b/i},
  {group:"Season rewards",label:"Quest Booster",rx:/quest booster/i},
  {group:"Season rewards",label:"Hero Coins",rx:/hero coins?/i},
  {group:"Cards",label:"Wild Supreme",rx:/wild supreme/i},
  {group:"Cards",label:"Wild Gold",rx:/wild gold/i},
  {group:"Cards",label:"Wild Any",rx:/wild any/i},
  {group:"Cards",label:"Wild Ace",rx:/wild ace/i},
  {group:"Cards",label:"Wild Ordinary",rx:/wild ordinary/i},
  {group:"Cards",label:"Wild card",rx:/\bwild\b/i},
  {group:"Cards",label:"Shiny Limited",rx:/shiny limited/i},
  {group:"Cards",label:"Shiny card",rx:/\bshiny\b|shiny card/i},
  {group:"Cards",label:"Gold card",rx:/\bgold\b|gold card/i},
  {group:"Cards",label:"Ace card",rx:/\bace\b|ace card/i},
  {group:"Cards",label:"Regular card / pack",rx:/\breg(?:ular)?\b|reg pack|card pack|\bpack\b|cards?/i},
  {group:"Special access",label:"48h machine access",rx:/48h|48 h|access|machine access/i},
  {group:"Special mechanics",label:"Prize wheel",rx:/wheel/i},
  {group:"Special mechanics",label:"Price cut",rx:/price cut/i},
  {group:"Removed / avoid",label:"Clan Pack (removed)",rx:/clan pack/i},
];
function detectPrizes(rawName){
  const s=String(rawName||"");
  const seen={};
  const out=[];
  PRIZE_PATTERNS.forEach(function(p){
    if(p.label==="Gold card"&&/gold gem stamp|\bGGS\b/i.test(s))return;
    if(p.label==="Ace card"&&/ace spins?/i.test(s))return;
    if(p.label==="Regular card / pack"&&/clan pack/i.test(s))return;
    if(p.label==="Wild card"&&/wild (supreme|gold|any|ace|ordinary)/i.test(s))return;
    if(p.rx.test(s)&&!seen[p.label]){
      seen[p.label]=true;
      out.push({group:p.group,label:p.label});
    }
  });
  return out;
}
function prizeChipsHtml(rawName, desc){
  const prizes=detectPrizes([rawName, desc].filter(Boolean).join("\n"));
  let h='<div class="sec-sub">Detected prizes from board item</div>';
  if(!prizes.length){
    return h+'<div class="line fitline">No explicit prize/content is written in this item name or description. Showing only the promo platform below; exact configured prizes must come from the board description/config, not from guessing.</div>';
  }
  h+='<div class="offer-parts prize-parts">';
  prizes.forEach(function(p){
    h+='<span class="offer-part prize-chip"><b>'+esc(p.group)+':</b> '+esc(p.label)+'</span>';
  });
  h+='</div>';
  return h;
}
function rollingCycleCount(rawName){
  const s=String(rawName||"");
  const m=s.match(/\b(\d+)\s*(?:cycles?|cyc(?:le)?s?)\b/i);
  if(m)return Math.max(1,Math.min(12,Number(m[1])||1));
  return 6;
}
function rollingTokens(text){
  return String(text||"")
    .replace(/[\u2000-\u200b\u202f\u205f\u3000]/g," ")
    .split(/\r?\n|\||;/)
    .map(function(x){return x.replace(/\s+/g," ").trim();})
    .filter(Boolean);
}
function parseRollingRows(text){
  const lines=rollingTokens(text);
  const rows=[];
  let currentCycle=null;
  let nextStep=1;
  function addRow(cycle,step,reward,globalStep){
    reward=String(reward||"").replace(/^[-–—:]+/,"").trim();
    if(!reward||/^rolling(?: offer)?$/i.test(reward)||/^buy more for less content:?$/i.test(reward))return;
    rows.push({
      globalStep:globalStep||((cycle-1)*6+step),
      step:step,
      cycle:cycle,
      reward:reward
    });
  }
  lines.forEach(function(line){
    let m=line.match(/^(?:rolling\s*)?cycle\s*(\d+)\b\s*[-–—:]?\s*(.*)$/i)||line.match(/^(\d+)\s*cycle\b\s*[-–—:]?\s*(.*)$/i);
    if(m){
      currentCycle=Number(m[1])||1;
      nextStep=1;
      const rest=(m[2]||"").trim();
      const firstRow=rest.match(/^(\d+)\s+(\d+)\s+(.+)$/);
      if(firstRow){
        const globalStep=Number(firstRow[1]);
        const step=Number(firstRow[2]);
        addRow(currentCycle,step,firstRow[3],globalStep);
        nextStep=Math.max(nextStep,step+1);
      }else if(rest){
        addRow(currentCycle,nextStep++,rest);
      }
      return;
    }
    m=line.match(/^(\d+)\s+(\d+)\s+(.+)$/);
    if(m){
      const globalStep=Number(m[1]);
      const step=Number(m[2]);
      const cycle=currentCycle||Math.ceil(globalStep/6);
      addRow(cycle,step,m[3],globalStep);
      nextStep=Math.max(nextStep,step+1);
      return;
    }
    if(currentCycle){
      addRow(currentCycle,nextStep++,line);
    }
  });
  return rows;
}
function parseRollingPayFreeRows(text){
  const lines=rollingTokens(text);
  const rows=[];
  let cycle=0;
  let step=0;
  function add(kind,content){
    content=String(content||"").replace(/^[-–—:]+/,"").trim();
    if(!content)return;
    rows.push({cycle:cycle,step:step,globalStep:rows.length+1,reward:kind+": "+content});
  }
  lines.forEach(function(line){
    let m=line.match(/^pay(?:\s+cash\s+denom|\s+with\s+sb)?\s*[-–—:]\s*(.+)$/i);
    if(m){
      cycle+=1;
      step=1;
      add("Pay",m[1]);
      return;
    }
    m=line.match(/^free\s*[-–—:]\s*(.+)$/i);
    if(m&&cycle){
      step+=1;
      add("Free",m[1]);
    }
  });
  return rows;
}
function parseRollingDenoms(text){
  const lines=rollingTokens(text);
  const rows=[];
  lines.forEach(function(line){
    let m=line.match(/^(?:denom|denoms?)\s*(\d+)?\s*[-–—:]\s*(.+)$/i);
    if(!m)m=line.match(/^(\d+)\.\s*(.+)$/);
    if(m){
      const label=m.length===3?(m[1]||String(rows.length+1)):m[1];
      const content=m.length===3?m[2]:m[2];
      rows.push({label:"Denom "+label,content:content.trim()});
      return;
    }
    m=line.match(/^((?:first|1st|2nd|3rd)\s+denom(?:\s*\([^)]*\))?|coins?\s+denoms?|gems?\s+denoms?)\s*[-–—:]\s*(.+)$/i);
    if(m)rows.push({label:m[1].replace(/\s+/g," "),content:m[2].trim()});
  });
  return rows;
}
function defaultRollingReward(step,cycle){
  if(step===1)return "Purchase/base slot: Coins/Gems + stamp slots (exact quantities not listed)";
  if(step===2)return "SlotoBucks % slot (exact % not listed)";
  if(step===3)return "Gameplay / season / card reward slot (exact reward not listed)";
  if(step===4)return "Hammers or alternate reward slot (exact amount not listed)";
  if(step===5)return "RDS / stamp slot (exact amount not listed)";
  if(step===6)return "GGS / stamp slot (exact amount not listed)";
  return "Reward slot";
}
function buildRollingStructureHtml(rawName, desc){
  const sourceText=[desc, rawName].filter(Boolean).join("\n");
  const explicitRows=parseRollingRows(sourceText);
  const payFreeRows=explicitRows.length?[]:parseRollingPayFreeRows(sourceText);
  const denomRows=(explicitRows.length||payFreeRows.length)?[]:parseRollingDenoms(sourceText);
  const cycleRows=explicitRows.length?explicitRows:payFreeRows;
  const cycleCount=cycleRows.length?Math.max.apply(null,cycleRows.map(function(r){return r.cycle;})):rollingCycleCount(sourceText);
  const rows=[];
  if(cycleRows.length){
    cycleRows.forEach(function(r){rows.push(r);});
  }else if(denomRows.length){
    let h='<div class="sec-sub">Rolling content structure</div>';
    h+='<div class="line fitline">Parsed from the real Monday description/name into denom → content. No reward quantities are inferred beyond the written text.</div>';
    h+='<div class="rolling-denoms"><table class="rank rolling-table"><thead><tr><th>Denom</th><th>Reward / content</th></tr></thead><tbody>';
    denomRows.forEach(function(r){h+='<tr><td>'+esc(r.label)+'</td><td>'+esc(r.content)+'</td></tr>';});
    h+='</tbody></table></div>';
    return h;
  }else{
    for(let c=1;c<=cycleCount;c++){
      for(let s=1;s<=6;s++){
        rows.push({globalStep:(c-1)*6+s,cycle:c,step:s,reward:defaultRollingReward(s,c),template:true});
      }
    }
  }
  const byCycle={};
  rows.forEach(function(r){(byCycle[r.cycle]||(byCycle[r.cycle]=[])).push(r);});
  let h='<div class="sec-sub">Rolling content structure</div>';
  if(cycleRows.length){
    h+='<div class="line fitline">Parsed from the real Monday description/name into '+(payFreeRows.length?'pay/free group':'cycle')+' → step → reward.</div>';
  }else{
    h+='<div class="line fitline">The board item does not list exact rewards; showing only the reusable Rolling slot map for '+cycleCount+' cycles. Quantities and exact prizes are intentionally not guessed.</div>';
  }
  h+='<div class="rolling-cycles">';
  Object.keys(byCycle).sort(function(a,b){return Number(a)-Number(b);}).forEach(function(cycle){
    h+='<div class="rolling-cycle"><div class="rolling-cycle-h">Cycle '+cycle+'</div>';
    h+='<table class="rank rolling-table"><thead><tr><th class="num">#</th><th class="num">Step</th><th>Reward / content</th></tr></thead><tbody>';
    byCycle[cycle].sort(function(a,b){return a.step-b.step;}).forEach(function(r){
      h+='<tr><td class="num">'+r.globalStep+'</td><td class="num">'+r.step+'</td><td>'+esc(r.reward)+(r.template?' <span class="muted">(template)</span>':'')+'</td></tr>';
    });
    h+='</tbody></table></div>';
  });
  h+='</div>';
  return h;
}
function decoyDenomLines(rawName, desc){
  const text=[rawName,desc].filter(Boolean).join("\n");
  const rows=[];
  const re=/\b(?:d|denom)\s*([123])\s*[:=\-—]\s*([^|\n]+)/gi;
  let m;
  while((m=re.exec(text))){
    rows.push({label:"Denom "+m[1],content:m[2].trim()});
  }
  if(rows.length>=2)return rows.slice(0,3);
  const re2=/\|\s*d([123]):\s*([^|]+)/gi;
  while((m=re2.exec(text))){
    rows.push({label:"Denom "+m[1],content:m[2].trim()});
  }
  if(rows.length>=2)return rows.slice(0,3);
  const full=text.match(/Full denoms:\s*(.+)/i);
  if(full){
    const chunk=full[1];
    const p2=/d([123]):\s*([^|]+)/gi;
    while((m=p2.exec(chunk))){
      rows.push({label:"Denom "+m[1],content:m[2].trim()});
    }
  }
  if(rows.length>=2)return rows.slice(0,3);
  const re3=/Denom\s*([123])\s*[-:–]\s*([^\n]+)/gi;
  while((m=re3.exec(text))){
    rows.push({label:"Denom "+m[1],content:m[2].trim()});
  }
  return rows.slice(0,3);
}
function buildDecoyBonanzaStructureHtml(rawName,desc){
  const rows=decoyDenomLines(rawName,desc);
  if(!rows.length)return "";
  let h='<div class="sec-sub">Decoy / Bonanza — denom contents</div>';
  h+='<div class="line fitline">Parsed from the item name/description — d2 is typically the deliberate decoy (middle denom).</div>';
  h+='<div class="rolling-denoms"><table class="rank rolling-table"><thead><tr><th>Denom</th><th>Rewards</th></tr></thead><tbody>';
  rows.forEach(function(r){
    h+='<tr><td>'+esc(r.label)+'</td><td>'+esc(r.content)+'</td></tr>';
  });
  return h+'</tbody></table></div>';
}
function buyAllDenomLines(rawName, desc){
  const text=[rawName,desc].filter(Boolean).join("\n");
  const rows=[];
  const coinsM=text.match(/Coins\s*(?:denom)?:\s*([^\n|]+)/i);
  const gemsM=text.match(/Gems\s*(?:denom)?:\s*([^\n|]+)/i);
  if(coinsM)rows.push({label:"Coins denom",content:coinsM[1].trim()});
  if(gemsM)rows.push({label:"Gems denom",content:gemsM[1].trim()});
  if(rows.length===2)return rows;
  const pipeC=text.match(/Coins:\s*([^|]+)/i);
  const pipeG=text.match(/\|\s*Gems:\s*([^|]+)/i);
  if(pipeC)rows.push({label:"Coins denom",content:pipeC[1].trim()});
  if(pipeG)rows.push({label:"Gems denom",content:pipeG[1].trim().replace(/\|\s*[HML]\s*Pricing.*$/i,"").trim()});
  return rows;
}
function buildBuyAllStructureHtml(rawName,desc){
  const rows=buyAllDenomLines(rawName,desc);
  if(rows.length<2)return "";
  let h='<div class="sec-sub">Buy All — two denoms (buy both)</div>';
  h+='<div class="line fitline">Coins+RDS base on denom 1 · Gems+GGS base on denom 2 — parsed from this item.</div>';
  h+='<div class="rolling-denoms"><table class="rank rolling-table"><thead><tr><th>Denom</th><th>Rewards</th></tr></thead><tbody>';
  rows.forEach(function(r){
    h+='<tr><td>'+esc(r.label)+'</td><td>'+esc(r.content)+'</td></tr>';
  });
  return h+'</tbody></table></div>';
}
function offerFamily(name,status){
  const s=(name||"").toLowerCase(), st=(status||"").toLowerCase();
  if(st==="rolling offer"||s.includes("rolling"))return /more.?for.?less|buy.?more/.test(s)?"rollingMoreForLess":"rollingBuyXGetY";
  if(st==="buy all"||s.includes("buy all")||s.includes("mystery buy all"))return"buyAll";
  if(st==="popup store"||s.includes("popup store"))return offerFamily(s.replace(/^popup store\s*[—–-]\s*/i,""),"");
  if(s.includes("decoy")||s.includes("bonanza")||s.includes("triple offer"))return"decoyBonanza";
  if(st==="daily deal"||s.startsWith("dd")||s.includes("daily deal"))return"dailyDeal";
  if(st==="ryd"||s.startsWith("ryd"))return"ryd";
  if(st==="prize mania"||s.includes("prize mania"))return"prizeMania";
  if(s.includes("stash bundle")||s.includes("surprise box"))return"stashBundle";
  if(/coins? sale/.test(s))return"coinSale";
  if(s.includes("mgap")){
    if(s.includes("bogo"))return"mgapBogo";
    if(s.includes("matched"))return"mgapMatched";
    if(s.includes("wild symbol"))return"mgapWildSymbols";
    if(s.includes("bigger"))return"mgapBigger";
    return"mgapOther";
  }
  if(s.includes("gemback"))return"gemback";
  if(s.includes("x2 ggs")||/\bggs\b/.test(s))return"ggs";
  if(s.includes("gems sale")||s.includes("gem sale"))return"gemsSale";
  if(s.includes("happy hour")||s.includes("jumbo")||s.includes("prize picker")||s.includes("eyes on")||s.includes("fortune dip"))return"happyHour";
  if(s.includes("extreme stamp"))return"extremeStamp";
  if(s.includes("custom pod"))return"customPod";
  if(s.includes("dice deluxe"))return"diceDeluxe";
  if(s.includes("dice booster")||s.includes("dice loot"))return"diceBooster";
  if(s.includes("shiny wolf"))return"shinyWolf";
  if(s.includes("growing shiny"))return"growingShiny";
  if(s.includes("shiny show"))return"shinyShow";
  if(s.includes("gold trading"))return"goldTrading";
  if(s.includes("loot"))return"loot";
  if(s.includes("pyp")||s.includes("pick your path"))return"pyp";
  if(s.includes("piggy"))return"piggy";
  if(s.includes("dash pass"))return"dashPass";
  if(s.includes("monday max"))return"mondayMax";
  if(s.includes("time limited"))return"timeLimited";
  if(s.includes("dash max"))return"dashMax";
  if(s.includes("power dash"))return"powerDash";
  if(s.includes("x2 dash"))return"x2Dash";
  if(s.includes("x2 badges")||s.includes("clan go"))return"clanGo";
  if(s.includes("slot smash"))return"slotSmash";
  if(s.includes("lotto"))return"lotto";
  if(st==="ads"||s.startsWith("ads"))return"ads";
  if(s.includes("golden spin"))return"goldenSpin";
  if(st==="counter po"||s.includes("counter po")||s.includes("limited po"))return"counterPo";
  if(s.includes("sneak peek"))return"sneakPeek";
  if(s.includes("machine launch")||s.includes("new machine")||s.includes("full launch"))return"machineLaunch";
  if(st==="black diamond"||s.includes("black diamond")||/^bd\b/.test(s))return"blackDiamond";
  if(s.includes("price cut"))return"priceCut";
  if(st==="core"||s.includes("core")||s.includes("mes")||s.includes("spin zone")||s.includes("win master")||s.includes("ace heist")||s.includes("spinner"))return"coreChallenge";
  if(st==="clan-dash"||s.includes("clan")||s.includes("dash"))return"clanDash";
  if(s.includes("scratch")||s.includes("slotobucks")||/%\s*sb\b/.test(s)||/\bsb\b/.test(s))return"slotoBucks";
  if(st==="event"||/\balbum (last|countdown)|where to get cards/.test(s))return"albumCountdown";
  // Generic, honest fallbacks by status: real board naming for short-window toppers/POs and
  // gem-machine mechanics is too varied to pattern-match exhaustively — rather than guessing
  // a specific mechanic, say plainly what category it is and point back at the parsed parts.
  if(st==="offers & coin sale")return"genericOffer";
  if(st==="gems")return"genericGem";
  return"other";
}
const FAMILY_INFO={
  rollingMoreForLess:{title:"Rolling More for Less",structure:"Platform: 3 all-inclusive denoms, value rises d1 < d2 < d3.",slots:"Allowed slot types: base currency, stamps, SlotoBucks %, and 1-2 reward-pool slots. Exact rewards must be detected from the item text/config.",note:"Flexible by goal: card push, hammers, gem pressure, or mixed. The sheet above is the actual detected content; this line is only the platform."},
  rollingBuyXGetY:{title:"Rolling Offer (Buy X Get Y)",structure:"Platform: one paid denom plus free denoms that unlock by cycle/step.",slots:"Allowed slot types: purchase/base slot, SlotoBucks %, stamps, and reward-pool slots. Exact rewards must be detected from the item text/config."},
  buyAll:{title:"Buy All",structure:"Platform: 2 denoms, buy both.",slots:"One denom is coin/red-stamp oriented; the other is gem/gold-stamp oriented. Extra reward slots are flexible and must be read from the actual item text/config."},
  decoyBonanza:{title:"Decoy / Bonanza / Triple Offer",structure:"Platform: 3 denoms — d1 Coins+RDS, d2 Gems+GGS (decoy middle). d3 = Coins+Gems+4 RDS+2 GGS + ALL prizes from d1 and d2 + one d3-only hook (Gold/Wild/SB…).",slots:"List d3 explicitly as ALL ABOVE + hook, or enumerate every d1/d2 SKU again on d3.",note:"The middle denom is the deliberate decoy; d3 must not drop d1/d2 side prizes."},
  dailyDeal:{title:"Daily Deal (DD)",structure:"Platform: Coins + Gems + one central SKU/reward slot, priced by tier.",slots:"Central slot can be any allowed reward from the pool; use the detected prizes above for this exact DD.",rule:"A DD offering Wild or Shiny Limited is once-per-player — must be paired with a second, repeatable DD so the player isn't left without an active deal."},
  ryd:{title:"RYD (Reveal Your Deal)",structure:"Platform: Coins + Gems + rotating hook + RDS + SlotoBucks %.",slots:"The hook/reward changes by instance; use the detected prizes above for the actual hook.",rule:"⛔ Never 155% SB — that was a one-time Cinco de Mayo value; standard tiers are 100/150/200%. Always pairs with a prize beyond SlotoBucks alone."},
  prizeMania:{title:"Prize Mania",structure:"Platform: bundled prize collection.",slots:"Flexible mix from the reward pool. Only detected prizes above should be treated as actual contents."},
  stashBundle:{title:"Stash Bundle / Surprise Box",structure:"Platform: one-time surprise box, once per player.",slots:"Flexible surprise-box contents. Only detected prizes above should be treated as actual contents."},
  coinSale:{title:"Coin Sale (segmented)",structure:"Coin injection, tiered by payer segment — feeds wager/economy.",slots:"Exact % tiers are not inferred here unless written in the item text/config."},
  mgapBogo:{title:"MGAP — BOGO",structure:"Coin multiplier: buy one multiplier tier, get a second free.",note:"The strongest MGAP variant in the data — #1 revenue engine flavor."},
  mgapMatched:{title:"MGAP — Matched",structure:"Coin multiplier matched to the size of the purchase.",note:"Strong while live, but revenue drops sharply once it ends — needs careful timing."},
  mgapBigger:{title:"MGAP — Bigger Multipliers",structure:"Coins at boosted multiplier tiers.",note:"Roughly neutral on a clean (non-holiday) day; strongest layered onto an already-big event day."},
  mgapWildSymbols:{title:"MGAP — Wild Symbols",structure:"Coin multiplier tied to Wild symbol hits, up to 500% SB.",note:"Weakest MGAP variant in the data — prefer BOGO when choosing a flavor."},
  mgapOther:{title:"MGAP",structure:"Coin multiplier promo — the #1 revenue engine family.",rule:"Exactly 2/week (iron — never >2); partial month tail week = 1. No Matched on sale; no BOGO on sale/last day."},
  gemback:{title:"Boosted Gemback",structure:"Gems back on all gem spend for a limited window.",note:"Broad amplifier — feeds the offer funnel + Payment Page more than any single product."},
  ggs:{title:"x2 Gold Gem Stamp",structure:"Doubles the Gold Gem Stamps earned in offers for a limited window.",rule:"Not the same day as a Gems Sale — cannibalizes it."},
  gemsSale:{title:"Gems Sale",structure:"Store-wide gem discount.",slots:"Exact discount % is not inferred unless written in the item text/config.",note:"Needs a gem-burn follow-up (Shiny Show) 24-48h later."},
  extremeStamp:{title:"Extreme Stamp",structure:"Upgrades the stamp in every offer that day.",slots:"Extreme Stamp replaces Red Diamond Stamp (RDS) — 4 RDS becomes 2 Extreme Stamps (higher value per stamp).",note:"A topper/amplifier, not a standalone driver — works best layered onto an already-big day."},
  customPod:{title:"Custom Pod",structure:"Core coin-sink tool.",slots:"Exact duration/multiplier is not inferred unless written in the item text/config."},
  diceDeluxe:{title:"Dice Deluxe",structure:"Coins at high multipliers, purchase-based.",note:"Needs an active dice source (from Dice Loot / Dice Booster) to convert — weak standalone."},
  diceBooster:{title:"Dice Booster / Loot",structure:"Time-limited dice multiplier or milestone loot.",note:"Booster: typically 12-24h, ≤3/week standalone."},
  shinyWolf:{title:"Shiny Wolf",structure:"High-odds guaranteed Shiny card mechanic."},
  growingShiny:{title:"Growing Shiny Show",structure:"3-act escalation.",slots:"Act 1: Wild Ordinary → Act 2: Wild Ace → Act 3: Wild Any."},
  shinyShow:{title:"Shiny Show",structure:"Gem-spend mini-game; complete acts to send a card to the album.",note:"Joker / All Cards / Wild Guaranteed variants burn the most gems (+89%/+57% vs baseline) — ~3/week cap."},
  goldTrading:{title:"Gold Trading Day",structure:"Album feature — trade/collect toward Gold-tier cards, tied to the active album week."},
  loot:{title:"Loot (Ace / Card / Dice)",structure:"Milestone ladder — more wins-in-a-row unlocks better prize tiers.",slots:"Exact card/prize tiers depend on the item text/config and weekly card bank."},
  pyp:{title:"PYP (Pick Your Path)",structure:"Complete 3 of 4 player-chosen tasks for a prize.",slots:"Example tasks: finish Shiny Show, open 3 pods, trigger free spins (gem machine), finish 3 dashes."},
  coreChallenge:{title:"Core gameplay challenge",structure:"Coin-sink challenge (Spin Zone / Win Master / Ace Heist / Spinner Clash / MES) — completion pays a prize from the weekly card bank.",rule:"No Gold cards in gameplay challenges — Gold is purchase-slot only."},
  piggy:{title:"Piggy",structure:"Break the piggy bank for a prize from the weekly bank."},
  dashPass:{title:"Dash Pass",structure:"Tiered season prizes (dash rewards) + a Time Limited Prize."},
  mondayMax:{title:"Monday Max Deal",structure:"Time Limited Prize: Superboom / card / picks."},
  timeLimited:{title:"Time Limited Prize",structure:"Superboom / card / 2 Airstrikes / picks — short window."},
  dashMax:{title:"Dash Max",structure:"Tiered dash-point prizes; exact point values come from the item text/config."},
  powerDash:{title:"Power Dash",structure:"PAB · picks · Dice Booster rewards."},
  x2Dash:{title:"x2 Dash Points",structure:"Double dash points earned that day."},
  clanGo:{title:"Clan Go / x2 Badges",structure:"Badge wheel — up to 200 badges, or Go Premium wheel."},
  slotSmash:{title:"Slot Smashes",structure:"New-machine-themed Clan-Dash prizes."},
  lotto:{title:"Lotto Bonus",structure:"Night Plan peak feature (Tue/Sat nights).",slots:"Exact Lotto boost must be read from the item text/config."},
  ads:{title:"ADS PO",structure:"Ad-based personal offer — lowest priority tier.",rule:"Low prizes only (Coins/Gems/low-tier reg cards). No high Gold/Ace/Wild/Shiny."},
  goldenSpin:{title:"Golden Spin",structure:"Bigger-multiplier spin feature.",rule:"Structurally the weakest promo in the data across every cut tested (-4.6% to -9.8% vs baseline) — don't rely on it to carry a day."},
  counterPo:{title:"Counter PO / Limited PO",structure:"Personal offer (topper); prize and pricing vary by payer segment."},
  sneakPeek:{title:"Sneak Peek",structure:"New-machine teaser — no prize, awareness only."},
  machineLaunch:{title:"Machine Launch",structure:"New machine day.",slots:"Launch-day extras are shown only when detected in the item/day content."},
  blackDiamond:{title:"Black Diamond",structure:"VIP-tier machine/offer — Inner Circle / high-value segment."},
  priceCut:{title:"Price Cut",structure:"Store-wide discount on pack pricing.",note:"Confirmed to lift both revenue and payers on a broad (non-segment-specific) cut."},
  clanDash:{title:"Clan-Dash",structure:"Payer-recruitment feature — badges, dash points, bundles.",note:"Monday = Dash Day (structural payer peak in the real data)."},
  happyHour:{title:"Happy Hour / Jumbo Giveaway",structure:"Short time-boxed window with boosted odds/value (Eyes on the Prize up to 700% Bucks, Jumbo Giveaway, Prize Picker, Fortune Dip).",note:"Amplifier for whatever else is running that window — priced +$15K in the revenue model (was $0), a real driver checked against 9 real days."},
  slotoBucks:{title:"SlotoBucks (SB)",structure:"Promo currency, non-redeemable — earned via offers/challenges.",slots:"Exact % tier is detected only if written in the item text/config.",rule:"⛔ 155% is a one-time legacy value (Cinco de Mayo) — don't reuse it."},
  albumCountdown:{title:"Album Countdown / Event Reminder",structure:"Non-purchase reminder/state item — album-end countdown, or a themed event marker.",note:"No slots of its own; check the same day's other promos (Gold Trading Day, Shiny Show, Coin Sale) for the actual player-facing offers."},
  genericOffer:{title:"Themed Offer / Topper",structure:"A short-window offer, topper, or segment-specific personal offer (PO) — real board naming for these is too varied to pattern-match to one exact mechanic.",note:"Common patterns: DPU/NPU-targeted POs, night-plan variants, event-themed toppers (Gatcha, LBP, World Cup, 4th of July). The parsed parts above show exactly what the item name states."},
  genericGem:{title:"Gem Mechanic",structure:"A gem-economy feature — spend booster, gem-machine promo, or stamp mechanic.",note:"Short-window amplifier layered on top of that day's main offers. The parsed parts above show the specific % or reward stated in the item."},
  other:{title:null,structure:null},
};
function descriptionHtml(desc){
  desc=compactOfferDescription(desc);
  if(!desc)return "";
  return '<div class="sec-sub">Contents &amp; prizes</div><div class="source-desc compact-desc">'+esc(desc)+'</div>';
}
function compactOfferDescription(desc){
  desc=String(desc||"").trim();
  if(!desc)return "";
  const lines=desc.split("\n").map(function(s){return s.trim();}).filter(Boolean);
  const out=[];
  const skipLine=/^(platform:|mechanic \(this instance\):|schedule:|purchase rule:|context:|rules:|pairing:|peak window:|rotation:|pricing: high|pricing: max)/i;
  lines.forEach(function(line){
    let m=line.match(/\(this instance\):\s*(.+)$/i);
    if(m){out.push(m[1]);return;}
    if(skipLine.test(line))return;
    if(/^Duration:/i.test(line)&&out.length>2)return;
    if(/^Gameplay Core —/i.test(line)){out.push(line.replace(/^Gameplay Core —\s*/i,""));return;}
    if(/^(d\d|full denoms|companion repeatable|once \+|coins denom|gems denom)/i.test(line))out.push(line);
    else if(line.length<220&&!/^Platform:/i.test(line))out.push(line);
  });
  const uniq=[];
  out.forEach(function(l){if(uniq.indexOf(l)<0)uniq.push(l);});
  return uniq.slice(0,14).join("\n");
}
function buildOfferSheetHtml(rawName,status,desc,pricing){
  const fam=offerFamily(rawName,status);
  const info=FAMILY_INFO[fam]||FAMILY_INFO.other;
  const parsed=parseOfferParts(rawName);
  const tier=pricing||resolveItemPricing({name:rawName,status:status,desc:desc});
  let h="";
  if(tier&&statusExpectsPricing(status,rawName))h+='<div class="offer-pricing-row">Pricing: <span class="price-pill price-pill-lg">'+esc(tier)+'</span></div>';
  h+=prizeChipsHtml(rawName,desc);
  const showParts=parsed.parts.length>1||(parsed.parts.length===1&&parsed.parts[0]!==String(rawName||"").trim());
  if(showParts){
    h+='<div class="sec-sub">This instance</div><div class="offer-parts">';
    parsed.parts.forEach(function(p){h+='<span class="offer-part">'+esc(p)+'</span>';});
    h+='</div>';
  }
  h+=descriptionHtml(desc);
  const metaBits=[];
  if(parsed.pricingTag&&!tier)metaBits.push("Pricing: "+(PRICE_LABEL[parsed.pricingTag.toLowerCase()]||parsed.pricingTag));
  if(parsed.timeWindow)metaBits.push("Window: "+parsed.timeWindow);
  if(metaBits.length)h+='<div class="offer-meta">'+metaBits.map(esc).join(" · ")+'</div>';
  if(fam==="rollingBuyXGetY"||fam==="rollingMoreForLess"||/\b\d+\s*(?:cycles?|cyc(?:le)?s?)\b/i.test([rawName,desc].filter(Boolean).join(" ")))h+=buildRollingStructureHtml(rawName,desc);
  if(fam==="decoyBonanza")h+=buildDecoyBonanzaStructureHtml(rawName,desc);
  if(fam==="buyAll")h+=buildBuyAllStructureHtml(rawName,desc);
  if(info.title&&(info.structure||info.rule)){
    h+='<details class="sheet-fold"><summary>Platform reference (optional)</summary>';
    if(info.structure)h+='<div class="line">'+esc(info.structure)+'</div>';
    if(info.slots)h+='<div class="line fitline">↳ '+esc(info.slots)+'</div>';
    if(info.note)h+='<div class="line fitline">↳ '+esc(info.note)+'</div>';
    if(info.rule)h+='<div class="offer-rule">⚠ '+esc(info.rule)+'</div>';
    h+='</details>';
  }
  if(!parsed.parts.length&&!info.structure&&!h.includes("prize-chip"))h+='<div class="line">'+esc(rawName)+'</div>';
  return h;
}
function esc(s){return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}

// ---- v7: self-calibrating model ----
// Every constant below used to be a number I hand-derived once via ad-hoc analysis scripts.
// Now they're all read from CALIBRATION, which scripts/calibrate_model.py recomputes FRESH
// from whatever real data exists in real_months.json every time the daily pipeline runs
// (scripts/daily_update.sh). As more real days get added day by day, these numbers — and
// therefore every prediction — update and improve automatically, with no manual re-tuning.
// Small-sample promo effects are shrunk toward the documented literature priors (empirical-
// Bayes style) so a promo seen only once or twice can't swing the whole model.
const CALIBRATION = __CALIBRATION__;
const REV_CAL = CALIBRATION.revenue || {};
const PU_CAL = CALIBRATION.pu || {};
const GAMEPLAY_CAL = CALIBRATION.gameplay || {};
const ECON_CAL = CALIBRATION.economy || {};
const CAL_META = CALIBRATION.meta || {};
const DRAFT_CALENDAR_MONTHS = new Set(CAL_META.draft_calendar_months || ["2026-08"]);
const DEFAULT_BASE_DOW_REV = {Sun:652,Mon:650,Tue:608,Wed:653,Thu:576,Fri:661,Sat:697};
const DEFAULT_BASE_DOW_PU = {Sun:29538,Mon:32972,Tue:24028,Wed:26752,Thu:23927,Fri:25153,Sat:27304};
function confLabel(entry){
  if(!entry)return"no calibration yet";
  if(entry.basis==="data")return"n="+entry.n;
  if(entry.basis==="blended")return"n="+entry.n+", blended w/ prior";
  return"prior, n=0 so far";
}
function pbRev(key){ const e=(REV_CAL.promo_bonus||{})[key]; return e?e.value:0; }
function pbRevWhy(key,label){ const e=(REV_CAL.promo_bonus||{})[key]; const v=e?e.value:0; return label+" "+(v>=0?"+":"")+v.toFixed(1)+"K ("+confLabel(e)+")"; }
const MAJOR_HOLIDAY_RE = /cinco de mayo|black friday|new year|valentine|st\.? ?patrick|independence day|4th of july|memorial day/i;

// The user base is shrinking (documented ~1-3%/month DAU decline, smart_calendar_insights.md
// §0/§4). For the current/mostly-unobserved month, a flat monthly crowd number would freeze
// the assumption at whatever the 1-2 real days so far show — instead we fit a continuous
// decline trend across the trailing real days (see calibrate_model.py) and extrapolate it
// forward day-by-day. Completed months just use their own flat empirical mean (n is large
// enough there for day-to-day promo noise to average out).
function crowdAdjustment(day, monthKey){
  const base=(REV_CAL.crowd_adj_by_month||{})[monthKey] ?? -10;
  if(monthKey===CAL_META.current_month && day.date>1){
    const slope=(REV_CAL.crowd_trend_per_day||{})[monthKey]||0;
    return base+slope*(day.date-1);
  }
  return base;
}
function puCrowdAdjustment(day, monthKey){
  const base=(PU_CAL.crowd_adj_by_month||{})[monthKey] ?? 0;
  if(monthKey===CAL_META.current_month && day.date>1){
    const slope=(PU_CAL.crowd_trend_per_day||{})[monthKey]||0;
    return base+slope*(day.date-1);
  }
  return base;
}

// ---- Promo-time boundary (CRITICAL) ----
// The daily plan changes at 13:00 UTC, but revenue is counted 00:00-24:00 UTC. So every
// calendar day's actual revenue is really two segments: 00:00-13:00 UTC (13h, still running
// YESTERDAY's plan) + 13:00-24:00 UTC (11h, running TODAY's own plan). A same-day promo bonus
// calibrated against real full-day revenue (like the ones below) already reflects that it only
// had ~11h of runtime on its own day — but it says NOTHING about the ~13h hangover it then
// creates on the FOLLOWING day's morning. That hangover was completely unmodeled before and is
// exactly why days after a big Coin Sale / event / cluster were under-predicted (e.g. Jun 21,
// the day after the Father's Day sale: predicted 624 vs actual 704, -13%).
const CARRYOVER_FRACTION = REV_CAL.carryover_fraction!=null?REV_CAL.carryover_fraction:0.4;
const ABSORPTION_PENALTY = REV_CAL.absorption_penalty!=null?REV_CAL.absorption_penalty:-18;
function getPrevDay(monthKey, dateNum){
  if(dateNum>1){
    const days=MONTHS[monthKey]||[];
    return days.find(function(d){return d.date===dateNum-1;})||null;
  }
  const idx=MONTH_KEYS.indexOf(monthKey);
  if(idx<=0)return null;
  const prevDays=MONTHS[MONTH_KEYS[idx-1]]||[];
  return prevDays.length?prevDays[prevDays.length-1]:null;
}
function liveItems(day){
  // Backup items are contingency promos prepped in case the primary plan underperforms —
  // not committed, so they must never feed the forecast. Already excluded from tag/sale/
  // banner detection at the data layer (pull_real_months.py); filtered again here so
  // anything reading day.items directly for prediction purposes stays consistent.
  return day.items.filter(function(x){return !x.backup;});
}
function ensurePurchaseDrivers(day){
  if(day.date!==1)return;
  day.purchaseDrivers=day.purchaseDrivers||[];
  if(!day.purchaseDrivers.some(function(d){return d.id==="month_open_biggest_denom";}))
    day.purchaseDrivers.push(Object.assign({},MONTH_OPEN_DENOM_DRIVER));
}
function purchaseDriversForDay(day){
  ensurePurchaseDrivers(day);
  return (day.purchaseDrivers||[]).filter(function(d){return d&&d.label;});
}
function purchaseDriverForecastNote(day){
  if(day.date!==1||!purchaseDriversForDay(day).length)return {bonus:0,why:[]};
  return {
    bonus:0,
    why:["1st-of-month biggest store denom — purchase baseline lift (purchase driver, not a board promo; month-open effect is mostly in the DOW/DOM forecast, not double-counted here)"],
  };
}
function normPricing(value){
  const s=String(value||"").trim().toLowerCase();
  if(s==="mid"||s==="medium"||s==="m")return"medium";
  if(s==="high"||s==="h")return"high";
  if(s==="max"||s==="maximum")return"max";
  return null;
}
function priceFamilyForItem(item){
  const name=String(item.name||"").toLowerCase();
  const status=String(item.status||"").toLowerCase();
  if(status==="daily deal"||/daily deal|^dd\b/.test(name))return"dailyDeal";
  if(status==="rolling offer"||/rolling/.test(name))return"rolling";
  if(status==="buy all"||/buy all|mystery buy all/.test(name))return"buyAll";
  if(status==="ryd"||/\bryd\b|reveal your deal/.test(name))return"ryd";
  if(/decoy|bonanza|triple offer/.test(name))return"decoyBonanza";
  return null;
}
function pricingEffect(day, cal, unitLabel){
  const map=cal.pricing_bonus||{};
  let value=0; const why=[];
  liveItems(day).forEach(function(item){
    const family=priceFamilyForItem(item);
    const tier=normPricing(item.pricing);
    if(!family||!tier)return;
    const key=family+":"+tier;
    const e=map[key];
    if(!e||!e.value)return;
    value+=e.value;
    const famLabel={dailyDeal:"Daily Deal",rolling:"Rolling Offer",decoyBonanza:"Decoy/Bonanza",ryd:"RYD",buyAll:"Buy All"}[family]||family;
    const tierLabel={medium:"Medium",high:"High",max:"Max"}[tier]||tier;
    why.push(famLabel+" "+tierLabel+" pricing "+(e.value>=0?"+":"")+e.value+(unitLabel==="K"?"K":"%")+" ("+confLabel(e)+")");
  });
  return {value:value, why:why};
}
function promoEffect(day){
  const it=liveItems(day).map(function(x){return x.name.toLowerCase();});
  const has=r=>it.some(i=>r.test(i));
  const mgapText=it.filter(function(t){return t.includes("mgap");}).join(" | ");
  const hasMgap=r=>r.test(mgapText);
  let bonus=0; const why=[];
  if(has(/custom pod/)){bonus+=pbRev("customPod");why.push(pbRevWhy("customPod","Custom Pod"));}
  if(has(/coins? sale/)){bonus+=pbRev("coinSale");why.push(pbRevWhy("coinSale","Coin Sale"));}
  if(has(/decoy|bonanza/)){bonus+=pbRev("decoyBonanza");why.push(pbRevWhy("decoyBonanza","Decoy/Bonanza"));}
  if(hasMgap(/bogo/)){bonus+=pbRev("mgapBogo");why.push(pbRevWhy("mgapBogo","MGAP BOGO"));}
  else if(hasMgap(/matched/)){bonus+=pbRev("mgapMatched");why.push(pbRevWhy("mgapMatched","MGAP Matched"));}
  else if(hasMgap(/wild symbol/)){bonus+=pbRev("mgapWildSymbols");why.push(pbRevWhy("mgapWildSymbols","MGAP Wild Symbols"));}
  else if(hasMgap(/bigger/)){bonus+=pbRev("mgapBigger");why.push(pbRevWhy("mgapBigger","MGAP Bigger"));}
  else if(mgapText){bonus+=pbRev("mgapOther");why.push(pbRevWhy("mgapOther","MGAP (other)"));}
  // Combo/interaction terms — calibrated from data (replaces hardcoded fixed terms)
  const hasCoinSale=has(/coins? sale/), hasCustomPod=has(/custom pod/), hasHappyHour=has(/happy hour|jumbo giveaway|jumbo|prize picker/), hasDecoy=has(/decoy|bonanza/);
  if(hasMgap(/./)&&hasCoinSale){bonus+=pbRev("ix_mgapBigger_x_coinSale");why.push(pbRevWhy("ix_mgapBigger_x_coinSale","MGAP×Sale interaction"));}
  if(hasCustomPod&&hasCoinSale){bonus+=pbRev("ix_customPod_x_coinSale");why.push(pbRevWhy("ix_customPod_x_coinSale","Custom Pod×Coin Sale synergy"));}
  if(hasCustomPod&&hasHappyHour){bonus+=pbRev("ix_customPod_x_happyHour");why.push(pbRevWhy("ix_customPod_x_happyHour","Custom Pod×Happy Hour synergy"));}
  if(hasCoinSale&&hasDecoy){bonus+=pbRev("ix_coinSale_x_decoyBonanza");why.push(pbRevWhy("ix_coinSale_x_decoyBonanza","Coin Sale×Decoy synergy"));}
  if(has(/gemback/)){bonus+=pbRev("gemback");why.push(pbRevWhy("gemback","Boosted Gemback"));}
  if(has(/more-for-less|more for less|buy-more/)){bonus+=pbRev("rollingMoreForLess");why.push(pbRevWhy("rollingMoreForLess","Rolling MoreForLess"));}
  else if(has(/rolling/)){bonus+=pbRev("rolling");why.push(pbRevWhy("rolling","Rolling"));}
  if(has(/prize mania/)){bonus+=pbRev("prizeMania");why.push(pbRevWhy("prizeMania","Prize Mania"));}
  if(has(/happy hour|jumbo giveaway|jumbo|prize picker/)){bonus+=pbRev("happyHour");why.push(pbRevWhy("happyHour","Happy Hour/Jumbo"));}
  if(has(/extreme stamp/)){bonus+=pbRev("extremeStamp");why.push(pbRevWhy("extremeStamp","Extreme Stamp"));}
  if(has(/fortune dip/)){bonus+=pbRev("fortuneDip");why.push(pbRevWhy("fortuneDip","Fortune Dip"));}
  if(has(/price cut/)){bonus+=pbRev("priceCut");why.push(pbRevWhy("priceCut","Price Cut"));}
  if(has(/buy all|mystery buy all/)){bonus+=pbRev("buyAll");why.push(pbRevWhy("buyAll","Buy All"));}
  if(has(/golden spin/)){bonus+=pbRev("goldenSpin");why.push(pbRevWhy("goldenSpin","Golden Spin"));}
  if(has(/counter po/)){bonus+=pbRev("counterPo");why.push(pbRevWhy("counterPo","Counter PO"));}
  if(has(/snl/)){bonus+=pbRev("snl");why.push(pbRevWhy("snl","SNL"));}
  // Item-count/breadth: even after pricing every named promo type above, more total items
  // still correlates with higher actual revenue — richer days cross-sell more than the sum
  // of their named parts. Small, capped, fixed shape (not auto-calibrated — a shape param
  // like this needs more structural care than a simple diff-in-means), skipped on "event"
  // days since the major/minor holiday bonus below already scales with item density there.
  const nLiveItems=it.length;
  if(day.tag!=="event"){
    const breadthExcess=Math.max(0,nLiveItems-8);
    if(breadthExcess>0){
      const b=Math.min(25,breadthExcess*2);
      bonus+=b; why.push("Promo breadth +$"+b+"K ("+nLiveItems+" items, fixed-shape term)");
    }
  }
  if(day.tag==="event"){
    // A flat bonus regardless of scale was the single biggest source of error early on: it
    // wildly over-shot light-touch days (Father's/Mother's Day, ~9-14 promos) and under-shot
    // flagship clusters (Cinco de Mayo, 23 promos). Scale by (a) whether it's a documented
    // flagship holiday and (b) how dense the real promo cluster is — both coefficients are
    // now fit from real event days (calibrate_model.py), falling back to the v6.2 hand-fit
    // shape when too few real event days exist yet.
    const eb=REV_CAL.event_bonus||{};
    const nItems=nLiveItems, excess=Math.max(0,nItems-9);
    const major=MAJOR_HOLIDAY_RE.test(day.banner||"");
    if(major){
      const m=eb.major||{floor:60,per_item:15,cap:300,n:0};
      let b=Math.min(m.cap,m.floor+m.per_item*excess);
      const nowcast=REV_CAL.current_month_nowcast||{};
      const inCurrentMonth=day.iso&&CAL_META.current_month&&day.iso.slice(0,7)===CAL_META.current_month;
      const factor=(inCurrentMonth&&nowcast.major_event_n>0)?(nowcast.major_event_factor||1):1;
      if(factor!==1){
        b*=factor;
        why.push("Major event/holiday adjusted to "+Math.round(factor*100)+"% of historical event curve after current-month actuals");
      }
      bonus+=b; why.push("Major event/holiday +$"+b.toFixed(0)+"K ("+nItems+" promos · "+(day.banner||"")+", n="+m.n+")");
    }else{
      const mi=eb.minor||{floor:0,per_item:4,cap:40,n:0};
      const b=Math.min(mi.cap,mi.per_item*excess);
      if(b>0){bonus+=b;why.push("Minor observance +$"+b.toFixed(0)+"K ("+nItems+" promos, n="+mi.n+")");}
      else why.push("Minor observance ("+(day.banner||"day")+") — no reliable uplift in the data, no bonus applied");
    }
  }
  if(day.tag==="machine"){
    const mc=(REV_CAL.event_bonus||{}).machine||{value:20,n:0};
    bonus+=mc.value; why.push("Machine launch +$"+mc.value.toFixed(0)+"K ("+(day.banner||"")+", n="+mc.n+")");
  }
  return {bonus, why, items:it, mgapText};
}
function predict(day, monthKey){
  // Empirical per-DOW average revenue, recomputed fresh from all real days every time the
  // pipeline runs (see CALIBRATION at the top) — falls back to the last-known-good v6.2
  // values if calibration is somehow missing.
  const BASE_DOW=(REV_CAL.base_dow&&Object.keys(REV_CAL.base_dow).length)?REV_CAL.base_dow:DEFAULT_BASE_DOW_REV;
  let rev=BASE_DOW[day.dow]||638, why=[];
  const adj=crowdAdjustment(day, monthKey);
  const nDow=(REV_CAL.n_dow||{})[day.dow];
  why.push("DOW+crowd base for "+(MONTH_LABEL[monthKey]||monthKey)+": $"+Math.round(BASE_DOW[day.dow])+"K"+(nDow!=null?" (n="+nDow+")":"")+" "+(adj>=0?"+":"")+Math.round(adj)+"K");
  rev+=adj;
  // Day-of-month curve: recomputed fresh from real data every pipeline run (mean residual
  // after DOW+crowd+promo, bucketed by day-of-month, shrunk toward 0 — see
  // calibrate_model.py's compute_day_of_month_curve). This REPLACED a hand-fixed
  // +25/+12/0/-10/0/-12 shape once 74 real days across 4 months showed it was actually
  // wrong-signed for week 1 (data says negative, not positive) and far too shallow for
  // month-end (data says ~-40K, not -12K). Cross-validated to cut error from 7.1%->6.4%.
  const domBucket=day.date<=2?"b1":day.date<=7?"b2":day.date<=14?"b3":day.date<=21?"b4":day.date<=28?"b5":"b6";
  const domCurve=REV_CAL.day_of_month_curve||{};
  const domLabel={b1:"Days 1-2 (month-open)",b2:"Days 3-7 (week 1)",b3:"Days 8-14 (week 2)",b4:"Days 15-21 (week 3)",b5:"Days 22-28 (week 4)",b6:"Month-end"};
  const domEntry=domCurve[domBucket];
  if(domEntry&&domEntry.value){
    rev+=domEntry.value;
    why.push(domLabel[domBucket]+" "+(domEntry.value>=0?"+":"")+domEntry.value+"K (n="+(domEntry.n||0)+" real days)");
  }

  const today=promoEffect(day);
  rev+=today.bonus;
  why.push.apply(why, today.why);
  const pdrv=purchaseDriverForecastNote(day);
  why.push.apply(why, pdrv.why);
  const priceToday=pricingEffect(day, REV_CAL, "K");
  if(priceToday.value){
    rev+=priceToday.value;
    why.push.apply(why, priceToday.why);
  }

  const prevDay=getPrevDay(monthKey, day.date);
  if(prevDay){
    const prev=promoEffect(prevDay);
    const prevPrice=pricingEffect(prevDay, REV_CAL, "K");
    const carry=Math.round((prev.bonus+prevPrice.value)*CARRYOVER_FRACTION);
    if(carry){
      rev+=carry;
      why.push("Promo-time carryover from "+prevDay.dow+" "+prevDay.date+" (00:00-13:00 UTC still ran yesterday's plan): "+(carry>=0?"+":"")+carry+"K");
    }
    // Post-sale absorption (low confidence, n=1 clean example): a plain, standalone Coin
    // Sale that ISN'T part of a branded multi-day event tends to leave a hangover the next
    // day — players already bought their coins, so the next day's own promo undersells even
    // with carryover already added. Checked: Jun 5 (Coin Sale) -> Jun 6 (Sat) missed by -$76K
    // despite Jun 6 having its own decent promos. Deliberately scoped to EXCLUDE branded
    // multi-day events (Lucy's Carnival day1->day2 showed the opposite — flat, no hangover —
    // so this only fires when yesterday's sale was a standalone day, not event/machine-tagged).
    const prevIsBrandedEvent=prevDay.items.some(function(i){return /carnival|\bdays? event\b|festival/i.test(i.name);});
    const prevWasPlainSale=prevDay.sale&&!prevDay.tag&&!prevIsBrandedEvent;
    if(prevWasPlainSale){
      rev+=ABSORPTION_PENALTY;
      why.push("Post-sale absorption after standalone Coin Sale on "+prevDay.dow+" "+prevDay.date+" "+ABSORPTION_PENALTY+"K (low confidence, n=1)");
    }
  }
  const nowcast=REV_CAL.current_month_nowcast||{};
  if(!day.actualRev&&monthKey===CAL_META.current_month&&nowcast.n>0&&nowcast.adjustment_k){
    rev+=nowcast.adjustment_k;
    why.push("Current-month nowcast correction "+(nowcast.adjustment_k>=0?"+":"")+nowcast.adjustment_k+"K (observed bias "+(nowcast.observed_bias_k>=0?"+":"")+nowcast.observed_bias_k+"K over "+nowcast.n+" actual days)");
  }
  rev=Math.max(400,Math.min(1300,Math.round(rev)));

  // Coin/gem pressure: tested against the 26 real June days with measured wager Δ%
  // (see banner note). Broad "is Core/Clan-Dash/RYD present" triggers were REMOVED here —
  // they're present on ~90%+ of all days regardless of outcome (gameplay sinks run daily),
  // so they added noise, not signal, and made the categorical guess *worse* than just
  // defaulting to "consumption dominates" every day. Result: this simplified version ties
  // the naive baseline (~50% match) — promo composition alone has weak explanatory power
  // for day-to-day wager swings; trust the measured magnitude over this arrow when both
  // are shown.
  const it=today.items;
  const has=r=>it.some(i=>r.test(i));
  const mgapText=today.mgapText;
  const coinInjected=has(/coins? sale/)||(mgapText&&/bogo|matched/.test(mgapText));
  const coinConsumed=has(/custom pod/)||has(/golden spin/);
  const coin=coinInjected&&!coinConsumed?1:(coinConsumed&&!coinInjected?-1:(coinInjected&&coinConsumed?0:-1));
  let gi=0,gc=0;
  if(has(/gemback/))gi+=2; if(has(/ggs/))gi+=1; if(has(/gems sale/))gi+=1;
  if(has(/shiny show|shiny wolf|growing shiny/))gc+=2;
  const gem=Math.max(-2,Math.min(2,gi-gc));
  return {rev, coin, gem, why};
}
// ---- PU (paying users) forecast ----
// Base + promo deltas all come from CALIBRATION.pu now, recomputed fresh every pipeline run.
// The DOW base is the cleanest signal in the whole model (e.g. Monday's real samples cluster
// tightly around ~33K, confirming "Monday = Dash Day = payer peak" structurally — no separate
// Dash bonus needed, it's already baked into the DOW baseline).
function predictPU(day, monthKey){
  const BASE_DOW=(PU_CAL.base_dow&&Object.keys(PU_CAL.base_dow).length)?PU_CAL.base_dow:DEFAULT_BASE_DOW_PU;
  let pu=BASE_DOW[day.dow]||27096, why=[];
  const adj=puCrowdAdjustment(day, monthKey);
  const nDow=(PU_CAL.n_dow||{})[day.dow];
  why.push("DOW+crowd base for "+(MONTH_LABEL[monthKey]||monthKey)+": "+Math.round(BASE_DOW[day.dow])+" PU"+(nDow!=null?" (n="+nDow+")":"")+" "+(adj>=0?"+":"")+Math.round(adj));
  pu+=adj;
  const it=liveItems(day).map(function(x){return x.name.toLowerCase();});
  const has=r=>it.some(i=>r.test(i));
  const mgapText=it.filter(function(t){return t.includes("mgap");}).join(" | ");
  let pct=0;
  const pbMap=PU_CAL.promo_bonus||{};
  function addPu(key,label){
    const e=pbMap[key]; if(!e)return;
    pct+=e.value; why.push(label+" "+(e.value>=0?"+":"")+e.value.toFixed(2)+"% PU ("+confLabel(e)+")");
  }
  if(has(/custom pod/))addPu("customPod","Custom Pod");
  if(has(/coins? sale/))addPu("coinSale","Coin Sale");
  if(/bogo/.test(mgapText))addPu("mgapBogo","MGAP BOGO");
  if(has(/buy all/))addPu("buyAll","Buy All");
  if(has(/golden spin/))addPu("goldenSpin","Golden Spin");
  if(has(/prize mania/))addPu("prizeMania","Prize Mania");
  if(has(/counter po/))addPu("counterPo","Counter PO");
  if(has(/rolling/))addPu("rolling","Rolling");
  const pricePu=pricingEffect(day, PU_CAL, "%");
  if(pricePu.value){
    pct+=pricePu.value;
    why.push.apply(why, pricePu.why);
  }
  if(pct){pu+=pu*pct/100;}
  // PU day-of-month curve (additive, fitted from data, shrunk toward 0)
  const puDomMap=PU_CAL.day_of_month_curve||{};
  const puDomKey=day.date<=2?"b1":day.date<=7?"b2":day.date<=14?"b3":day.date<=21?"b4":day.date<=28?"b5":"b6";
  const puDomAdj=(puDomMap[puDomKey]||{}).value||0;
  if(puDomAdj){pu+=puDomAdj;why.push("PU day-of-month curve ["+puDomKey+"] "+(puDomAdj>=0?"+":"")+Math.round(puDomAdj)+" PU");}
  const nowcast=PU_CAL.current_month_nowcast||{};
  if(!day.actualPU&&monthKey===CAL_META.current_month&&nowcast.n>0&&nowcast.adjustment_pct){
    pu+=pu*nowcast.adjustment_pct/100;
    why.push("Current-month PU nowcast correction "+(nowcast.adjustment_pct>=0?"+":"")+nowcast.adjustment_pct.toFixed(2)+"% (observed bias "+(nowcast.observed_bias_pct>=0?"+":"")+nowcast.observed_bias_pct.toFixed(2)+"% over "+nowcast.n+" actual days)");
  }
  pu=Math.max(15000,Math.min(40000,Math.round(pu)));
  return {pu, why};
}
// ---- Gameplay forecast (spins / win-rate / sessions) ----
// Thinnest data in the whole model: the only real gameplay numbers we have are the same 21
// exact DWH days used for revenue/PU's base (no live DB access to extend it, no promo-level
// deltas computed — the correlation analysis run earlier found composition alone explains
// very little of day-to-day gameplay variance). DOW-only baseline, explicitly labeled low-n.
function predictGameplay(day){
  const base=(GAMEPLAY_CAL.base_dow||{})[day.dow];
  const n=GAMEPLAY_CAL.n_days||0;
  if(!base||base.spinners==null)return null;
  return {
    spinners: base.spinners, spinsPerSpinner: base.spinsPerSpinner,
    winRate: base.winRate, sessionsPerUser: base.sessionsPerUser, n: n,
  };
}
// ---- PU coin/gem balance forecast (numeric, not just direction) ----
// New signal (added once real PU-segment balance data was pulled live from DWH — see
// pull_real_months.py's load_pu_balance and calibrate_model.py's compute_economy_curve):
// Median % change in Active-PU coin/gem balance, end-of-day vs prior end-of-day.
// Cross-validated finding: sink/status composition barely moves this beyond the DOW baseline
// (current held-out error is shown in the day sheet from calibration metadata) —
// so the promo deltas below are real but small (heavily shrunk), and the DOW baseline is
// doing almost all the work. Treat any single day's "miss" against this forecast as normal
// noise, not a broken model — day-to-day spread is large and still mostly unexplained.
function economyPromoDelta(day, cal){
  const names=live_namesJS(day);
  const seasonStatuses=(day.seasons||[]).map(function(s){return s.status;});
  let total=0; const hits=[];
  const table=cal.promo_delta||{};
  Object.keys(table).forEach(function(key){
    let present=false;
    if(key==="shortTerm")present=seasonStatuses.indexOf("Short Term")>=0;
    else if(key==="midTerm")present=seasonStatuses.indexOf("Mid Term")>=0;
    else if(key==="album")present=seasonStatuses.indexOf("Album")>=0;
    else {
      const pat=ECON_RX[key]; if(!pat)return;
      present=pat.test(names.join(" | "));
    }
    if(present){ const v=table[key].value||0; if(v){ total+=v; hits.push(key); } }
  });
  return {delta: total, hits: hits};
}
function live_namesJS(day){
  return (day.items||[]).filter(function(i){return !i.backup;}).map(function(i){return i.name.toLowerCase();});
}
// Mirrors calibrate_model.py's economy sink/status keys, not revenue purchase-offer families.
const ECON_RX = {
  pyp:/\bpyp\b|pick your path/,
  mesTokens:/\bmes\b|m\.e\.s|mega event store|tokens?|steps?/,
  spinnerClash:/spinner clash/,
  aceCardLoot:/ace loot|card loot|loot/,
  customPod:/custom pod/,
  clanPoints:/clan|badges?/,
  dashChallenge:/dash/,
  machine:/machine|launch|sneak peek/,
  winMaster:/win master/,
  spinZone:/spin zone/,
  jackpot:/jackpot/,
  megaWinner:/mega winner/,
  shinyShow:/shiny show|growing shiny|shiny wolf/
};
function predictEconomy(day){
  const coinBase=(ECON_CAL.coin_pct_base_dow||{})[day.dow];
  const gemBase=(ECON_CAL.gem_pct_base_dow||{})[day.dow];
  if(coinBase==null&&gemBase==null)return null;
  const coinD=economyPromoDelta(day,{promo_delta:ECON_CAL.coin_pct_promo_delta});
  const gemD=economyPromoDelta(day,{promo_delta:ECON_CAL.gem_pct_promo_delta});
  return {
    coinPct: coinBase!=null?Math.round((coinBase+coinD.delta)*10)/10:null,
    gemPct: gemBase!=null?Math.round((gemBase+gemD.delta)*10)/10:null,
    coinN: (ECON_CAL.coin_pct_n_dow||{})[day.dow]||0,
    gemN: (ECON_CAL.gem_pct_n_dow||{})[day.dow]||0,
    coinCvSpread: ECON_CAL.coin_cv_full_pp, gemCvSpread: ECON_CAL.gem_cv_full_pp,
    coinHits: coinD.hits, gemHits: gemD.hits,
  };
}
function dirClass(v){ return v>=1?"up":v<=-1?"dn":"flat"; }
function dirLabel(v,name){ const a=v>=1?"↑":v<=-1?"↓":"→"; return (name?name+" ":"")+a; }
function matchIcon(predCls,actual){
  if(!actual)return"";
  const map={up:"up",dn:"down",flat:"stable"};
  return map[predCls]===actual?" ✓":" ✗";
}
function resolveItemPricing(item){
  const raw=item&&(item.pricing!=null?item.pricing:"");
  if(raw&&String(raw).trim())return String(raw).trim();
  const parsed=parseOfferParts(item&&item.name||"");
  if(parsed.pricingTag)return PRICE_LABEL[parsed.pricingTag.toLowerCase()]||parsed.pricingTag;
  const desc=item&&item.desc||"";
  const dm=desc.match(/Pricing:\s*(High|Max|Medium|Mid|Low)/i);
  if(dm)return dm[1]==="Mid"?"Medium":dm[1];
  const nm=(item&&item.name||"").match(/\|\s*(H|M|L)\s*Pric(?:e|ing)/i);
  if(nm){const m={h:"High",m:"Medium",l:"Low"};return m[nm[1].toLowerCase()]||nm[1];}
  return "";
}
function statusExpectsPricing(status, name){
  const st=(status||"").toLowerCase();
  const nm=(name||"").toLowerCase();
  if(st==="clan-dash")return false;
  if(st==="mgap"||/^mgap\b/.test(nm))return false;
  if(/time limited prize/i.test(nm))return false;
  if(/clan[- ]dash bundle/i.test(nm)||st==="clan-dash bundle")return false;
  if(/^piggy\b/i.test(nm))return false;
  if(/dice deluxe|dice promo/i.test(nm))return false;
  if(/fortune dip/i.test(nm))return false;
  if(/coin sale/i.test(nm))return false;
  if(st==="counter po"||/^counter po\b/i.test(nm))return false;
  if(/price cut/i.test(nm))return false;
  if(st==="popup store")return false;
  return /daily deal|ryd|buy all|rolling offer|prize mania|offers & coin sale|segmented test|clan-dash/.test(st)
    ||(/^decoy bonanza|^buy all|^ryd|^rolling offer|^prize mania/i.test(nm));
}
function itemExpectsPricing(item){
  if(!item)return false;
  return statusExpectsPricing(item.status, item.name);
}
function pricingBadgeHtml(pricing){
  if(!pricing)return "";
  return ' <span class="price-pill">'+esc(pricing)+'</span>';
}
function cleanLabel(t){
  t=String(t||"");
  if(/decoy bonanza|triple offer/i.test(t)&&/\bd3:/i.test(t)){
    const m=t.match(/—\s*d3:\s*([^|+]+)/i);
    const top=m?m[1].trim():"bundle";
    const isTest=/triple offer/i.test(t);
    return (isTest?"Triple Offer TEST":"Decoy Bonanza")+" · d3 "+top;
  }
  if(/^buy all\s*-/i.test(t)&&/coins:/i.test(t))return "Buy All — 2 denoms (Coins + Gems)";
  return t.replace(/\s*\([^)]*\)/g,"").replace(/\s*→.*$/,"").replace(/\s{2,}/g," ").trim();
}

const CAT_ORDER = {offers:0, mgap:1, dd:2, gems:3, anchor:4, core:5, gameplay:6, ads:7};
const CAT_GROUP = {offers:"money", mgap:"money", dd:"money", gems:"money", anchor:"anchor", core:"gameplay", gameplay:"gameplay", ads:"ads"};
let calDisplayMode = "all";
let calSearchQuery = "";

function sortedItems(items){
  return items.map(function(it,i){
    return {
      t:it.name, desc:it.desc||"", i:i,
      c:it.cat||classify(it.name),
      status:it.status||"",
      pricing:resolveItemPricing(it),
      backup:!!it.backup, userEdited:!!it.userEdited,
    };
  }).sort(function(a,b){return (CAT_ORDER[a.c]??4)-(CAT_ORDER[b.c]??4);});
}
function itemMatchesSearch(ent){
  if(!calSearchQuery)return true;
  const q=calSearchQuery.toLowerCase();
  const hay=[ent.t, ent.desc, cleanLabel(ent.t), CAT_LABEL[ent.c]||"", ent.c].join(" ").toLowerCase();
  return hay.indexOf(q)>=0;
}
function filterItemEntry(ent){
  if(calDisplayMode==="compact"&&ent.c==="ads")return false;
  if(calDisplayMode==="money"&&(ent.c==="gameplay"||ent.c==="core"||ent.c==="ads"))return false;
  if(!itemMatchesSearch(ent))return false;
  return true;
}
function seasonsBlockHtml(day){
  if(!day.seasons||!day.seasons.length)return '<div class="seasons seasons-cell seasons-empty">No season item logged on the board for this day</div>';
  return '<div class="seasons seasons-cell">'+day.seasons.map(function(s,i){
    var col=SEASON_COLOR[s.status]||"#8b96ad", ab=SEASON_ABBR[s.status]||s.status;
    var firstBadge=s.isFirst?'<span class="season-first-badge" title="First day of this season">★</span>':'';
    return '<div class="srow srow-click" data-d="'+day.date+'" data-si="'+i+'" title="Click for details'+(s.isFirst?' · First day of season':'')+'">'
      +'<span class="stag" style="background:'+col+'28;color:'+col+';border-color:'+col+'88">'+ab+'</span>'
      +'<span class="sval">'+esc(s.name)+firstBadge+'</span></div>';
  }).join("")+"</div>";
}
function revClass(rev){
  if(rev>=690)return"rev-hot";
  if(rev>=640)return"rev-mid";
  if(rev<=610)return"rev-cool";
  return"";
}
function accuracyClass(deltaPct){
  const a=Math.abs(deltaPct);
  if(a<=8)return"acc-good";
  if(a<=20)return"acc-mid";
  return"acc-bad";
}
function revSourceLabel(src){
  if(src==="exact")return"DWH exact";
  if(src==="estimated")return"estimated (opening read × typical DOW ratio, low confidence)";
  return"team diary, approx";
}
function fmtSigned(n,unit,digits){
  if(n==null)return"";
  const v=digits?n.toFixed(digits):Math.round(n);
  return(n>=0?"+":"")+v+unit;
}
// Direction shown here now prioritizes REAL data over the weak promo-composition heuristic:
// - If we have a measured actual (velocity, day-over-day close vs close) for this day, show
//   that direction — it's ground truth, not a guess.
// - Otherwise fall back to the DOW+regression economy forecast (predictEconomy), which is
//   cross-validated and far more honest than the old promo-name heuristic (pr.coin/pr.gem,
//   ~46-50% match rate against real outcomes — barely better than a coin flip).
function economyCellView(day){
  const eco=predictEconomy(day);
  const haveCoinActual=day.coinMagnitude!=null&&day.coinSource==="active_pu_balance_dwh";
  const haveGemActual=day.gemMagnitude!=null&&day.gemSource==="active_pu_balance_dwh";
  const coinDir=haveCoinActual?dirClass(day.coinActual==="up"?1:day.coinActual==="down"?-1:0):(eco&&eco.coinPct!=null?dirClass(eco.coinPct>=5?1:eco.coinPct<=-5?-1:0):"flat");
  const gemDir=haveGemActual?dirClass(day.gemActual==="up"?1:day.gemActual==="down"?-1:0):(eco&&eco.gemPct!=null?dirClass(eco.gemPct>=5?1:eco.gemPct<=-5?-1:0):"flat");
  const coinTxt=haveCoinActual?fmtSigned(day.coinMagnitude,"%",1):(eco&&eco.coinPct!=null?fmtSigned(eco.coinPct,"%",1)+"e":"");
  const gemTxt=haveGemActual?fmtSigned(day.gemMagnitude,"%",1):(eco&&eco.gemPct!=null?fmtSigned(eco.gemPct,"%",1)+"e":"");
  return {coinDir, gemDir, coinTxt, gemTxt, haveCoinActual, haveGemActual};
}
function formatPredFooter(pr,day){
  const ev=economyCellView(day);
  const coinLab='Coin '+(ev.coinDir==="up"?"↑":ev.coinDir==="dn"?"↓":"→");
  const gemLab='Gems '+(ev.gemDir==="up"?"↑":ev.gemDir==="dn"?"↓":"→");
  const coinMag=ev.coinTxt?' <b class="magv">'+ev.coinTxt+'</b>':"";
  const gemMag=ev.gemTxt?' <b class="magv">'+ev.gemTxt+'</b>':"";
  const title=ev.haveCoinActual||ev.haveGemActual?"Real PU balance velocity (day-over-day) — click for detail":"Forecast (DOW+promo model, 'e'=estimate) — click for detail";
  return '<div class="pred" data-date="'+pr.date+'" title="'+title+'">'
    +'<span class="pred-hint">'+((ev.haveCoinActual||ev.haveGemActual)?"Real":"Forecast")+'</span>'
    +'<span class="'+ev.coinDir+'">'+coinLab+coinMag+'</span>'
    +'<span class="'+ev.gemDir+'">'+gemLab+gemMag+'</span></div>';
}

function fmtPU(n){ return (n/1000).toFixed(1)+"K"; }
// SM coin balances run into extreme hyperinflation (trillions to undecillions are NORMAL,
// not errors — see workspace rules on SM coin hyperinflation). Format with the right suffix
// rather than dumping raw exponential notation on the user.
const BIG_SUFFIXES=[[1e33,"Dc"],[1e30,"No"],[1e27,"Oc"],[1e24,"Sp"],[1e21,"Sx"],[1e18,"Qi"],[1e15,"Qa"],[1e12,"T"],[1e9,"B"],[1e6,"M"],[1e3,"K"]];
function fmtBig(n){
  if(n==null)return"—";
  for(let i=0;i<BIG_SUFFIXES.length;i++){
    if(n>=BIG_SUFFIXES[i][0])return(n/BIG_SUFFIXES[i][0]).toFixed(2)+BIG_SUFFIXES[i][1];
  }
  return Math.round(n).toLocaleString();
}
function smartCheckMeta(day){
  const sc=day.smartCalendarCheck||{};
  const status=sc.status||"unknown";
  if(status==="matched")return {cls:"ok",label:"SC match",title:"Monday and Smart Calendar family keys match"};
  if(status==="mismatch")return {cls:"warn",label:"SC diff",title:"Smart Calendar and Monday differ; open day for details"};
  if(status==="smart_only")return {cls:"warn",label:"SC only",title:"Smart Calendar has live promos not present in Monday day column"};
  if(status==="monday_only")return {cls:"muted",label:"Monday only",title:"No Smart Calendar cache for this day or not live at snapshot"};
  if(status==="no_smart_data")return {cls:"muted",label:"No SC",title:"No Smart Calendar cache for this day"};
  return {cls:"muted",label:"SC ?",title:"Smart Calendar check unavailable"};
}
function smartCheckHtml(day){
  const sc=day.smartCalendarCheck||{};
  const meta=smartCheckMeta(day);
  const smart=(sc.smartKeys||[]).length;
  const monday=(sc.mondayKeys||[]).length;
  let h='<div class="sc-check sc-'+meta.cls+'"><div><b>'+esc(meta.label)+'</b><span>Monday '+monday+' families · Smart '+smart+' families</span></div>';
  const missM=sc.missingInMondayLabels||[];
  const missS=sc.missingInSmartLabels||[];
  if(missM.length)h+='<p><strong>Live in Smart, not in Monday column:</strong> '+missM.map(esc).join(", ")+'</p>';
  if(missS.length)h+='<p><strong>In Monday column, not live in Smart snapshot:</strong> '+missS.map(esc).join(", ")+'</p>';
  if(!missM.length&&!missS.length)h+='<p>Family-level check is aligned. Monday remains the source for exact text/content; Smart Calendar validates live scheduled families.</p>';
  h+='</div>';
  return h;
}
function buildCellHtml(day, monthKey){
  const pr=predict(day, monthKey);
  pr.date=day.date;
  const puPr=predictPU(day, monthKey);
  const wk=Math.ceil(day.date/7);
  const all=sortedItems(day.items);
  const visible=all.filter(filterItemEntry);
  const queryMatched=!calSearchQuery||all.some(itemMatchesSearch)||String(day.banner||"").toLowerCase().indexOf(calSearchQuery.toLowerCase())>=0||(day.seasons||[]).some(function(s){return String(s.name||"").toLowerCase().indexOf(calSearchQuery.toLowerCase())>=0;});
  let html='';
  html+='<button type="button" class="chead-open" data-date="'+day.date+'" aria-label="Open day '+day.date+' overview">';
  html+='<div class="chead">';
  html+='<div class="cdate-wrap"><span class="cdate'+(day.tag?" spec":"")+'">'+day.date+'</span><span class="cdow">'+day.dow+'</span></div>';
  html+='<div class="chead-badges">';
  if(day.sale)html+='<span class="pill sale">SALE</span>';
  const scMeta=smartCheckMeta(day);
  if((day.smartCalendarCheck||{}).status)html+='<span class="pill sc-mini '+scMeta.cls+'" title="'+esc(scMeta.title)+'">'+scMeta.label+'</span>';
  html+='<span class="rev-chip '+revClass(pr.rev)+'">$'+pr.rev+'K<i>fcst</i></span>';
  if(day.actualRev){
    const actK=Math.round(day.actualRev/1000);
    const deltaPct=Math.round((actK-pr.rev)/pr.rev*100);
    html+='<span class="rev-chip actual'+(day.revSource==="estimated"?" is-estimated":"")+' '+accuracyClass(deltaPct)+'" title="Actual $'+actK+'K · '+revSourceLabel(day.revSource)+'">$'+actK+'K '+(day.revSource==="estimated"?"est.":"real")+'<i>'+(deltaPct>=0?"+":"")+deltaPct+'%</i></span>';
  }
  html+='</div></div>';
  html+='<div class="pu-row" title="Predicted paying users">';
  html+='<span class="pu-chip">'+fmtPU(puPr.pu)+' PU<i>fcst</i></span>';
  if(day.actualPU){
    const puDelta=Math.round((day.actualPU-puPr.pu)/puPr.pu*100);
    html+='<span class="pu-chip actual '+accuracyClass(puDelta)+'" title="Actual '+fmtPU(day.actualPU)+' PU · '+(day.puSource==="exact"?"DWH exact":"team diary, approx")+'">'+fmtPU(day.actualPU)+' real<i>'+(puDelta>=0?"+":"")+puDelta+'%</i></span>';
  }
  html+='</div>';
  if(day.banner)html+='<div class="ribbon">'+esc(day.banner)+'</div>';
  if(day.date===1&&purchaseDriversForDay(day).length){
    html+='<div class="driver-ribbon" title="Purchase driver — not counted as a board promo">🛒 '+esc(purchaseDriversForDay(day)[0].label)+'</div>';
  }
  html+='</button>';
  html+=seasonsBlockHtml(day);
  html+='<div class="items">';
  visible.forEach(function(ent){
    var col=CAT_COLOR[ent.c];
    html+='<div class="item'+(ent.backup?" is-backup":"")+(ent.userEdited?" is-edited":"")+'" data-d="'+day.date+'" data-i="'+ent.i+'" style="--lane:'+col+'" title="'+(ent.backup?"Backup / contingency — not counted in the forecast":ent.userEdited?"You edited this promo (saved in this browser)":"")+'">'
      +'<span class="idot" style="background:'+col+'"></span><span class="t">'+esc(cleanLabel(ent.t))+(itemExpectsPricing({status:ent.status,name:ent.t})&&ent.pricing?pricingBadgeHtml(ent.pricing):"")+(ent.userEdited?' <b class="edited-tag">EDITED</b>':'')+(ent.backup?' <b class="backup-tag">BACKUP</b>':'')+'</span></div>';
  });
  if(calSearchQuery&&!visible.length){
    html+='<div class="empty-match">No visible promo match</div>';
  }
  html+='</div>';
  html+=formatPredFooter(pr,day);
  return {html:html, wk:wk, special:!!day.tag, matchCount:visible.length, queryMatched:queryMatched};
}

function renderCalendarGrid(){
  const grid=document.getElementById("grid");
  if(!grid)return;
  const days=MONTHS[currentMonthKey]||[];
  grid.innerHTML="";
  WEEKDAYS.forEach(function(w){const e=document.createElement("div");e.className="whead";e.textContent=w;grid.appendChild(e);});
  const firstDow=days.length?new Date(days[0].iso+"T00:00:00").getDay():0;
  for(let i=0;i<firstDow;i++){const b=document.createElement("div");b.className="cell blank";grid.appendChild(b);}
  days.forEach(function(day){
    const built=buildCellHtml(day, currentMonthKey);
    const c=document.createElement("div");
    c.className="cell"+(built.special?" special":"")+" wk-"+built.wk+(day.isPast?" is-past":"")+(calSearchQuery?(built.matchCount?" search-hit":" search-dim"):"");
    c.dataset.date=String(day.date);
    c.innerHTML=built.html;
  grid.appendChild(c);
});
  const status=document.getElementById("cal-search-status");
  if(status){
    if(!calSearchQuery)status.textContent="";
    else {
      const matches=days.reduce(function(sum,d){return sum+buildCellHtml(d,currentMonthKey).matchCount;},0);
      status.textContent=matches?matches+" matching items":"No matching visible items";
    }
  }
}

function isDraftCalendarMonth(monthKey){
  return DRAFT_CALENDAR_MONTHS.has(monthKey);
}
function renderDraftBanner(){
  const el=document.getElementById("cal-draft-banner");
  if(!el)return;
  if(!isDraftCalendarMonth(currentMonthKey)){
    el.hidden=true;
    el.textContent="";
    return;
  }
  el.hidden=false;
  calUpdateEditBanner();
}

function renderMonthTabs(){
  const bar=document.getElementById("month-tabs");
  if(!bar)return;
  bar.innerHTML=MONTH_KEYS.map(function(mk){
    const n=(MONTHS[mk]||[]).length;
    const draft=isDraftCalendarMonth(mk);
    const lab=MONTH_LABEL[mk]||mk;
    return '<button type="button" class="mbtn'+(mk===currentMonthKey?" active":"")+(draft?" is-draft":"")+'" data-month="'+mk+'">'
      +(draft?lab.replace(" 2026","")+" · draft":lab)
      +' <span class="mn">'+n+'d</span></button>';
  }).join("");
  bar.querySelectorAll(".mbtn").forEach(function(btn){
    btn.addEventListener("click",function(){
      if(btn.dataset.month===currentMonthKey)return;
      currentMonthKey=btn.dataset.month;
      renderMonthTabs();
      renderDraftBanner();
      renderCalendarGrid();
      renderCalStats();
    });
  });
}

function renderCalStats(){
  const days=MONTHS[currentMonthKey]||[];
  const cs=document.getElementById("calstats");
  if(!cs)return;
  let sumRev=0, sumPU=0, saleDays=0, events=0, machines=0, accSum=0, accCount=0, puAccSum=0, puAccCount=0;
  let fullMonthRev=0, fullMonthPU=0, fullMonthActualRevDays=0, fullMonthActualPUDays=0;
  let actRevSum=0, actRevDays=0, actPUSum=0, actPUDays=0, actRevSource=null, actPUSource=null;
  days.forEach(function(d){
    const pr=predict(d, currentMonthKey);
    const puPr=predictPU(d, currentMonthKey);
    sumRev+=pr.rev; sumPU+=puPr.pu;
    fullMonthRev+=(d.actualRev?d.actualRev/1000:pr.rev);
    fullMonthPU+=(d.actualPU?d.actualPU:puPr.pu);
    if(d.sale)saleDays++;
    if(d.tag==="event")events++;
    if(d.tag==="machine")machines++;
    if(d.actualRev){
      const actK=d.actualRev/1000;
      accSum+=Math.abs((actK-pr.rev)/pr.rev*100);
      accCount++;
      actRevSum+=actK; actRevDays++;
      fullMonthActualRevDays++;
      if(d.revSource==="estimated")actRevSource="estimated";
    }
    if(d.actualPU){
      puAccSum+=Math.abs((d.actualPU-puPr.pu)/puPr.pu*100);
      puAccCount++;
      actPUSum+=d.actualPU; actPUDays++;
      fullMonthActualPUDays++;
      if(d.puSource!=="exact")actPUSource="approx";
    }
  });
  const avg=Math.round(sumRev/(days.length||1));
  const avgPU=Math.round(sumPU/(days.length||1));
  const fullMonthAvgPU=Math.round(fullMonthPU/(days.length||1));
  const revFullLabel=fullMonthActualRevDays===days.length?'Actual revenue (full month, DWH)':'Full-month revenue (DWH actual + forecast)';
  const puFullLabel=fullMonthActualPUDays===days.length?'Actual avg payers (full month, DWH)':'Full-month avg payers (DWH actual + forecast)';
  const kpi=(v,l,c)=>'<div class="kpi"><div class="v"'+(c?' style="color:'+c+'"':'')+'>'+v+'</div><div class="l">'+l+'</div></div>';
  let html="";
  if(isDraftCalendarMonth(currentMonthKey)){
    html+=kpi("Draft","Plan source: guidelines — no Monday board","#fbbf24");
  }
  html+=kpi('$'+(sumRev/1000).toFixed(1)+'M','Forecast revenue (month total)','#22c55e')
    +kpi('$'+(fullMonthRev/1000).toFixed(1)+'M'+(actRevSource?'*':''),revFullLabel+(actRevSource?' · * some est.':''),'#4ade80')
    +kpi('$'+avg+'K','Daily average (forecast)')
    +kpi(fmtPU(avgPU)+' PU','Daily average payers (forecast)','#c084fc')
    +kpi(fmtPU(fullMonthAvgPU)+' PU',puFullLabel+(actPUSource?' · approx fallback used':''),'#e9d5ff')
    +kpi(days.length+' days · '+saleDays+' sale days','Coverage')
    +kpi(events+' events · '+machines+' machine launches','Peak anchors');
  if(accCount){
    const avgErr=accSum/accCount;
    html+=kpi('±'+Math.round(avgErr)+'%',accCount+' days w/ real revenue — avg forecast error',avgErr<=10?'#22c55e':avgErr<=20?'#eab308':'#ef4444');
  }
  if(puAccCount){
    const avgPuErr=puAccSum/puAccCount;
    html+=kpi('±'+Math.round(avgPuErr)+'%',puAccCount+' days w/ real PU — avg forecast error',avgPuErr<=10?'#22c55e':avgPuErr<=20?'#eab308':'#ef4444');
  }
  cs.innerHTML=html;
}

// ---- Calendar promo edits (localStorage per month; EDITED marker on grid) ----
function calEditsKey(monthKey){return CAL_EDIT_PREFIX+monthKey;}
function calLoadEditsBlob(monthKey){
  try{const raw=localStorage.getItem(calEditsKey(monthKey));return raw?JSON.parse(raw):null;}catch(e){return null;}
}
function calSaveEditsBlob(monthKey,blob){
  try{localStorage.setItem(calEditsKey(monthKey),JSON.stringify(blob));}catch(e){}
}
function calSnapshotDay(day){
  return {
    items:day.items.map(function(it){
      return {
        name:it.name,
        status:it.status||"",
        pricing:it.pricing!=null?it.pricing:"",
        desc:it.desc||"",
        backup:!!it.backup,
        userEdited:!!it.userEdited,
      };
    }),
    planNotes:day.planNotes||"",
    purchaseDrivers:(day.purchaseDrivers||[]).map(function(d){return Object.assign({},d);}),
  };
}
function calInitEdits(){
  MONTH_KEYS.forEach(function(mk){
    const blob=calLoadEditsBlob(mk);
    if(!blob||!blob.days)return;
    (MONTHS[mk]||[]).forEach(function(day){
      const patch=blob.days[String(day.date)];
      if(!patch)return;
      if(patch.items)day.items=patch.items;
      if(patch.planNotes!=null)day.planNotes=patch.planNotes;
      if(patch.purchaseDrivers)day.purchaseDrivers=patch.purchaseDrivers;
    });
  });
  MONTH_KEYS.forEach(function(mk){
    (MONTHS[mk]||[]).forEach(ensurePurchaseDrivers);
  });
}
function calPersistDay(monthKey,day){
  const blob=calLoadEditsBlob(monthKey)||{days:{}};
  blob.days[String(day.date)]=calSnapshotDay(day);
  calSaveEditsBlob(monthKey,blob);
  calUpdateEditBanner();
}
function calNewItem(name,status,pricing,desc){
  return {name:name,status:status,pricing:pricing||"",desc:desc||"",backup:false,userEdited:true};
}
function calAfterDayEdit(day){
  calPersistDay(currentMonthKey,day);
  renderCalendarGrid();
  renderCalStats();
}
function calEditedItemCount(monthKey){
  return (MONTHS[monthKey]||[]).reduce(function(n,d){
    return n+d.items.filter(function(i){return i.userEdited;}).length;
  },0);
}
function calResetMonthEdits(monthKey){
  if(!CAL_BASELINE[monthKey])return;
  localStorage.removeItem(calEditsKey(monthKey));
  MONTHS[monthKey]=JSON.parse(JSON.stringify(CAL_BASELINE[monthKey]));
  calUpdateEditBanner();
  renderCalendarGrid();
  renderCalStats();
}
function calExportEditedMonth(monthKey){
  const days=MONTHS[monthKey]||[];
  const blob=new Blob([JSON.stringify({month:monthKey,editedLocally:true,days:days},null,2)],{type:"application/json"});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob);
  a.download="mm_calendar_"+monthKey+"_edited.json";
  a.click();
}
function calUpdateEditBanner(){
  const el=document.getElementById("cal-draft-banner");
  if(!el||!isDraftCalendarMonth(currentMonthKey))return;
  const n=calEditedItemCount(currentMonthKey);
  const base="Built from <code>monthly_guidelines/2026-08.md</code> + <code>august_2026_plan.json</code>. "
    +"<b>Not on Monday</b> — forecast revenue/PU only. "
    +"Regenerate: <code>python3 scripts/build_august_2026_plan.py</code> then <code>build_calendar_html.py</code>.";
  if(n){
    el.innerHTML="<b>August 2026 — local review draft.</b> "+base
      +" <b>"+n+" promo line(s) marked EDITED</b> (saved in this browser only). "
      +"Open a day → <b>Edit promos</b> at the bottom. "
      +"<button type=\"button\" class=\"ux-action cal-inline-btn\" id=\"cal-banner-reset\">Restore generated plan</button>";
    const btn=document.getElementById("cal-banner-reset");
    if(btn)btn.addEventListener("click",function(){if(confirm("Discard all local promo edits for this month?"))calResetMonthEdits(currentMonthKey);});
  }else{
    el.innerHTML="<b>August 2026 — local review draft.</b> "+base
      +" <span style=\"color:var(--mut)\">Open any day → <b>Edit promos</b> to add/remove/change lines (marked EDITED).</span>";
  }
}
function calDayEditorHtml(day){
  const rows=day.items.map(function(item,idx){
    return '<div class="cal-edit-row" data-idx="'+idx+'">'
      +'<input type="text" data-field="name" value="'+esc(item.name)+'" placeholder="Promo name"/>'
      +'<select data-field="status">'+CAL_ITEM_STATUSES.map(function(s){
        return '<option'+(s===(item.status||"")?" selected":"")+'>'+s+'</option>';
      }).join("")+'</select>'
      +'<select data-field="pricing">'+CAL_PRICING_OPTIONS.map(function(p){
        return '<option value="'+p+'"'+(String(item.pricing||"")===p?" selected":"")+'>'+(p||"—")+'</option>';
      }).join("")+'</select>'
      +'<button type="button" class="cal-edit-remove" data-remove="'+idx+'" title="Remove promo">✕</button>'
      +(item.userEdited?'<span class="edited-tag edited-tag-inline">EDITED</span>':"")
      +'<textarea data-field="desc" rows="2" placeholder="Description / notes">'+esc(item.desc||"")+'</textarea>'
      +'</div>';
  }).join("");
  return '<div class="cal-edit-panel" id="cal-edit-panel">'
    +'<div class="sheet-section-title">Edit promos <span class="cal-edit-hint">Auto-saved · EDITED badge on grid</span></div>'
    +'<div class="cal-edit-rows">'+rows+'</div>'
    +'<div class="cal-edit-add">'
    +'<input type="text" id="cal-new-name" placeholder="New promo name"/>'
    +'<select id="cal-new-status">'+CAL_ITEM_STATUSES.map(function(s,i){
      return '<option'+(i===1?" selected":"")+'>'+s+'</option>';
    }).join("")+'</select>'
    +'<select id="cal-new-pricing">'+CAL_PRICING_OPTIONS.map(function(p){
      return '<option value="'+p+'">'+(p||"—")+'</option>';
    }).join("")+'</select>'
    +'<button type="button" class="pl-btn" id="cal-add-item">+ Add promo</button>'
    +'</div>'
    +'<label class="pl-field">Day notes<textarea id="cal-day-notes" rows="2">'+esc(day.planNotes||"")+'</textarea></label>'
    +'<div class="cal-edit-actions">'
    +'<button type="button" class="pl-btn ghost" id="cal-export-month">Export month JSON</button>'
    +'<button type="button" class="pl-btn ghost" id="cal-reset-month">Restore generated plan</button>'
    +'</div></div>';
}
function calBindDayEditor(day){
  const panel=document.getElementById("cal-edit-panel");
  if(!panel)return;
  panel.querySelectorAll(".cal-edit-row").forEach(function(row){
    const idx=Number(row.dataset.idx);
    function touch(reopen){
      const it=day.items[idx];
      if(!it)return;
      it.userEdited=true;
      row.querySelectorAll("[data-field]").forEach(function(inp){
        it[inp.dataset.field]=inp.value;
      });
      calAfterDayEdit(day);
      if(!row.querySelector(".edited-tag-inline")){
        const sp=document.createElement("span");
        sp.className="edited-tag edited-tag-inline";
        sp.textContent="EDITED";
        const rm=row.querySelector(".cal-edit-remove");
        if(rm)rm.insertAdjacentElement("afterend",sp);
      }
      if(reopen)openDaySheet(day);
    }
    row.querySelectorAll("input[data-field],select[data-field],textarea[data-field]").forEach(function(inp){
      inp.addEventListener("change",function(){touch(false);});
      if(inp.tagName==="INPUT"||inp.tagName==="TEXTAREA")inp.addEventListener("blur",function(){touch(false);});
    });
  });
  panel.querySelectorAll("[data-remove]").forEach(function(btn){
    btn.addEventListener("click",function(e){
      e.stopPropagation();
      day.items.splice(Number(btn.dataset.remove),1);
      calAfterDayEdit(day);
      openDaySheet(day);
    });
  });
  const addBtn=document.getElementById("cal-add-item");
  if(addBtn)addBtn.addEventListener("click",function(){
    const name=(document.getElementById("cal-new-name").value||"").trim();
    if(!name)return;
    day.items.push(calNewItem(
      name,
      document.getElementById("cal-new-status").value,
      document.getElementById("cal-new-pricing").value,
      ""
    ));
    calAfterDayEdit(day);
    openDaySheet(day);
  });
  const notesEl=document.getElementById("cal-day-notes");
  if(notesEl)notesEl.addEventListener("change",function(){
    day.planNotes=notesEl.value;
    calPersistDay(currentMonthKey,day);
  });
  const resetBtn=document.getElementById("cal-reset-month");
  if(resetBtn)resetBtn.addEventListener("click",function(){
    if(confirm("Discard all local edits for "+(MONTH_LABEL[currentMonthKey]||currentMonthKey)+"?")){
      calResetMonthEdits(currentMonthKey);
      closeSheet();
    }
  });
  const exportBtn=document.getElementById("cal-export-month");
  if(exportBtn)exportBtn.addEventListener("click",function(){calExportEditedMonth(currentMonthKey);});
}

function openDaySheet(day){
  const pr=predict(day, currentMonthKey);
  const puPr=predictPU(day, currentMonthKey);
  const ecoPr=predictEconomy(day);
  let h='<div class="sheet sheet-day"><button class="close">Close ✕</button>';
  h+='<div class="sheet-day-hdr"><div><span class="sheet-day-num">'+day.date+'</span> <span class="sheet-day-dow">'+day.dow+'</span> <span class="sheet-day-month">'+(MONTH_LABEL[currentMonthKey]||"")+'</span></div>';
  h+='<div class="sheet-rev-wrap"><div class="sheet-rev '+revClass(pr.rev)+'">$'+pr.rev+'K <span class="sheet-rev-lab">forecast</span></div>'
    +'<div class="sheet-pu">'+fmtPU(puPr.pu)+' PU <span class="sheet-rev-lab">forecast</span></div></div></div>';
  if(day.banner)h+='<div class="ribbon sheet-ribbon">'+esc(day.banner)+'</div>';
  if(day.planNotes)h+='<div class="sheet-tip">📝 '+esc(day.planNotes)+'</div>';
  const backupCount=day.items.filter(function(i){return i.backup;}).length;
  const live=sortedItems(day.items).filter(function(e){return !e.backup;});
  const moneyCount=live.filter(function(e){return CAT_GROUP[e.c]==="money";}).length;
  const gameplayCount=live.filter(function(e){return CAT_GROUP[e.c]==="gameplay";}).length;
  const anchorCount=live.filter(function(e){return CAT_GROUP[e.c]==="anchor";}).length;
  h+='<div class="sheet-summary-grid">'
    +'<div class="sheet-summary"><b>'+live.length+'</b><span>live items</span></div>'
    +'<div class="sheet-summary"><b>'+moneyCount+'</b><span>money</span></div>'
    +'<div class="sheet-summary"><b>'+gameplayCount+'</b><span>gameplay</span></div>'
    +'<div class="sheet-summary"><b>'+anchorCount+'</b><span>anchors</span></div>'
    +'</div>';
  const pricedMoney=live.filter(function(e){return itemExpectsPricing({status:e.status,name:e.t})&&e.pricing;});
  if(pricedMoney.length){
    h+='<p class="sheet-tip sheet-pricing-tip">Offer tiers: '+pricedMoney.map(function(e){
      return esc(cleanLabel(e.t).slice(0,36))+' '+e.pricing;
    }).join(" · ")+'</p>';
  }
  if(backupCount)h+='<p class="sheet-tip">⚠ '+backupCount+' backup item'+(backupCount>1?"s":"")+' (not in forecast).</p>';
  if(day.actualRev||day.actualPU||day.coinActual||day.gemActual){
    h+='<details class="sheet-fold"><summary>Actual vs forecast (optional)</summary><div class="avp-list">';
    if(day.actualRev){
      const actK=Math.round(day.actualRev/1000);
      const deltaPct=Math.round((actK-pr.rev)/pr.rev*100);
      h+='<div class="avp-row"><span class="avp-lab">Revenue</span><span class="avp-vals">forecast $'+pr.rev+'K → actual $'+actK+'K <b class="'+accuracyClass(deltaPct)+'">('+(deltaPct>=0?"+":"")+deltaPct+'%)</b></span><span class="avp-src">'+revSourceLabel(day.revSource)+'</span></div>';
    }
    if(day.actualPU){
      const puDeltaPct=Math.round((day.actualPU-puPr.pu)/puPr.pu*100);
      h+='<div class="avp-row"><span class="avp-lab">Payers (PU)</span><span class="avp-vals">forecast '+fmtPU(puPr.pu)+' → actual '+fmtPU(day.actualPU)+' <b class="'+accuracyClass(puDeltaPct)+'">('+(puDeltaPct>=0?"+":"")+puDeltaPct+'%)</b></span><span class="avp-src">'+(day.puSource==="exact"?"DWH exact":"team diary (approx)")+'</span></div>';
    }
    if(day.coinMagnitude!=null&&day.coinSource==="active_pu_balance_dwh"){
      const predTxt=ecoPr&&ecoPr.coinPct!=null?fmtSigned(ecoPr.coinPct,"%",1):"n/a";
      const deltaPp=ecoPr&&ecoPr.coinPct!=null?(day.coinMagnitude-ecoPr.coinPct):null;
      const spread=ecoPr?ecoPr.coinCvSpread:null;
      const withinNoise=spread!=null&&deltaPp!=null&&Math.abs(deltaPp)<=spread;
      h+='<div class="avp-row"><span class="avp-lab">Active PU coin velocity</span><span class="avp-vals">predicted '+predTxt+' → actual '+fmtSigned(day.coinMagnitude,"%",1)
        +(deltaPp!=null?' <b class="'+(withinNoise?"acc-good":"acc-bad")+'">('+(deltaPp>=0?"+":"")+deltaPp.toFixed(1)+'pp'+(withinNoise?", within noise":"")+')</b>':'')
        +'</span><span class="avp-src">day-over-day, DWH exact · Active PU balance segment (n='+(day.puCount||"?")+') · DOW baseline n='+(ecoPr?ecoPr.coinN:0)+'</span></div>';
      if(day.coinSameDayPct!=null){
        h+='<div class="avp-row avp-raw"><span class="avp-lab">Same-day balance move</span><span class="avp-vals">'+fmtSigned(day.coinSameDayPct,"%",1)+'</span><span class="avp-src">start→end of day for Active PU; secondary diagnostic only, velocity above is the planning signal</span></div>';
      }
    }else if(day.coinActual){
      const magTxt=day.coinMagnitude!=null?' — '+fmtSigned(day.coinMagnitude,"%",1)+' ('+(day.coinMagLabel||"")+')':'';
      h+='<div class="avp-row"><span class="avp-lab">Coin balance</span><span class="avp-vals">predicted '+dirLabel(pr.coin,"")+' → actual '+day.coinActual+magTxt+matchIcon(dirClass(pr.coin),day.coinActual)+'</span><span class="avp-src">inferred (ops notes)</span></div>';
    }
    if(day.gemMagnitude!=null&&day.gemSource==="active_pu_balance_dwh"){
      const predTxt=ecoPr&&ecoPr.gemPct!=null?fmtSigned(ecoPr.gemPct,"%",1):"n/a";
      const deltaPp=ecoPr&&ecoPr.gemPct!=null?(day.gemMagnitude-ecoPr.gemPct):null;
      const spread=ecoPr?ecoPr.gemCvSpread:null;
      const withinNoise=spread!=null&&deltaPp!=null&&Math.abs(deltaPp)<=spread;
      h+='<div class="avp-row"><span class="avp-lab">Active PU gem velocity</span><span class="avp-vals">predicted '+predTxt+' → actual '+fmtSigned(day.gemMagnitude,"%",1)
        +(deltaPp!=null?' <b class="'+(withinNoise?"acc-good":"acc-bad")+'">('+(deltaPp>=0?"+":"")+deltaPp.toFixed(1)+'pp'+(withinNoise?", within noise":"")+')</b>':'')
        +'</span><span class="avp-src">day-over-day, DWH exact · Active PU balance segment (n='+(day.puCount||"?")+') · DOW baseline n='+(ecoPr?ecoPr.gemN:0)+'</span></div>';
      if(day.gemSameDayPct!=null){
        h+='<div class="avp-row avp-raw"><span class="avp-lab">Same-day balance move</span><span class="avp-vals">'+fmtSigned(day.gemSameDayPct,"%",1)+'</span><span class="avp-src">start→end of day for Active PU; secondary diagnostic only, velocity above is the planning signal</span></div>';
      }
    }else if(day.gemActual){
      const magTxt=day.gemMagnitude!=null?' — '+fmtSigned(day.gemMagnitude,"M",0)+' ('+(day.gemMagLabel||"")+')':'';
      h+='<div class="avp-row"><span class="avp-lab">Gem balance</span><span class="avp-vals">predicted '+dirLabel(pr.gem,"")+' → actual '+day.gemActual+magTxt+matchIcon(dirClass(pr.gem),day.gemActual)+'</span><span class="avp-src">inferred (ops notes)</span></div>';
    }
    if(day.coinBalanceStart!=null){
      h+='<div class="avp-row avp-raw"><span class="avp-lab">Active PU coin balance (median, raw)</span><span class="avp-vals">'+fmtBig(day.coinBalanceStart)+' → '+fmtBig(day.coinBalanceEnd)+'</span><span class="avp-src">start of day → end of day</span></div>';
    }
    if(day.gemBalanceStart!=null){
      h+='<div class="avp-row avp-raw"><span class="avp-lab">Active PU gem balance (median, raw)</span><span class="avp-vals">'+Math.round(day.gemBalanceStart).toLocaleString()+' → '+Math.round(day.gemBalanceEnd).toLocaleString()+'</span><span class="avp-src">start of day → end of day</span></div>';
    }
    h+='</div></details>';
  }
  h+='<div class="sheet-section-title">Scheduled board content</div>';
  const pdrv=purchaseDriversForDay(day);
  if(pdrv.length){
    h+='<div class="purchase-drivers-block">';
    h+='<div class="sec-sub">Purchase drivers <span class="cal-edit-hint">(lift revenue/PU — not board promos)</span></div>';
    pdrv.forEach(function(dr){
      h+='<div class="purchase-driver-row"><span class="driver-dot"></span><div><b>'+esc(dr.label)+'</b>'
        +(dr.desc?'<p class="sheet-tip">'+esc(compactOfferDescription(dr.desc))+'</p>':"")+'</div></div>';
    });
    h+='</div>';
  }
  h+=smartCheckHtml(day);
  h+='<div class="sec-sub">Season rhythm</div>';
  if(day.seasons&&day.seasons.length){
    day.seasons.forEach(function(s,si){
      var col=SEASON_COLOR[s.status]||"#8b96ad";
      h+='<button type="button" class="srow sheet-srow sheet-srow-btn" data-si="'+si+'" style="border-color:transparent"><span class="stag" style="background:'+col+'22;color:'+col+';border-color:'+col+'66">'+(SEASON_ABBR[s.status]||s.status)+'</span><span class="sval">'+esc(s.name)+'</span></button>';
    });
  }else{
    h+='<p class="sheet-tip">No season item logged on the board for this day.</p>';
  }
  const groups=[["money","Monetization"],["anchor","Anchors / events"],["gameplay","Gameplay / Core"],["ads","ADS"]];
  groups.forEach(function(g){
    const list=sortedItems(day.items).filter(function(e){return CAT_GROUP[e.c]===g[0];});
    if(!list.length)return;
    h+='<div class="sec-sub">'+g[1]+'</div><div class="sheet-items">';
    list.forEach(function(ent){
      h+='<button type="button" class="sheet-item'+(ent.backup?" is-backup":"")+(ent.userEdited?" is-edited":"")+'" data-d="'+day.date+'" data-i="'+ent.i+'">'
        +'<span class="idot" style="background:'+CAT_COLOR[ent.c]+'"></span><span>'+esc(cleanLabel(ent.t))+(itemExpectsPricing({status:ent.status,name:ent.t})&&ent.pricing?pricingBadgeHtml(ent.pricing):"")+(ent.userEdited?' <b class="edited-tag">EDITED</b>':'')+(ent.backup?' <b class="backup-tag">BACKUP</b>':'')+'</span></button>';
    });
    h+='</div>';
  });
  h+='<details class="sheet-fold"><summary>Forecast drivers (optional)</summary>';
  h+='<div class="sec-sub">Revenue</div><ul class="why-list">';
  pr.why.forEach(function(w){h+='<li>'+esc(w)+'</li>';});
  h+='</ul>';
  if(puPr.why.length){
    h+='<div class="sec-sub">PU</div><ul class="why-list">';
    puPr.why.forEach(function(w){h+='<li>'+esc(w)+'</li>';});
    h+='</ul>';
  }
  const gp=predictGameplay(day);
  if(gp){
    h+='<div class="sec-sub">Gameplay (DOW baseline, n='+gp.n+')</div>';
    h+='<div class="gp-grid">'
      +'<div class="gp-cell"><div class="gp-v">'+(gp.spinners/1000).toFixed(0)+'K</div><div class="gp-l">Spinners</div></div>'
      +'<div class="gp-cell"><div class="gp-v">'+gp.spinsPerSpinner+'</div><div class="gp-l">Spins / spinner</div></div>'
      +'<div class="gp-cell"><div class="gp-v">'+gp.winRate+'%</div><div class="gp-l">Win rate</div></div>'
      +'<div class="gp-cell"><div class="gp-v">'+gp.sessionsPerUser+'</div><div class="gp-l">Sessions / user</div></div>'
      +'</div>';
  }
  h+='</details>';
  h+='<p class="sheet-tip">Click a promo below for prizes &amp; SKU breakdown.</p>';
  h+=calDayEditorHtml(day);
  h+='</div>';
  detail.innerHTML=h;
  detail.style.display="flex";
  detail.querySelector(".close").addEventListener("click",closeSheet);
  calBindDayEditor(day);
  detail.querySelectorAll(".sheet-item").forEach(function(btn){
    btn.addEventListener("click",function(){
      const it=day.items[btn.dataset.i];
      openSheet(cleanLabel(it.name),it.name,day,day.date+" · "+day.dow,it.status,it.desc,resolveItemPricing(it));
    });
  });
  detail.querySelectorAll(".sheet-srow-btn").forEach(function(btn){
    btn.addEventListener("click",function(){
      const s=day.seasons[btn.dataset.si];
      openSheet(cleanLabel(s.name),s.name,day,day.date+" · "+day.dow+" · "+(SEASON_ABBR[s.status]||s.status),s.status,s.desc);
    });
  });
}

// ---- render calendar ----
const legend=document.getElementById("legend");
if(legend){
  const groups=[["money","Monetization"],["anchor","Rhythm / album"],["gameplay","Gameplay"],["ads","ADS"]];
  let legHtml="";
  groups.forEach(function(g){
    legHtml+='<div class="leg-group"><div class="leg-title">'+g[1]+'</div><div class="leg-items">';
    Object.keys(CAT_LABEL).forEach(function(k){
      if(CAT_GROUP[k]!==g[0])return;
      legHtml+='<span><i class="dot" style="background:'+CAT_COLOR[k]+'"></i>'+CAT_LABEL[k]+'</span>';
    });
    legHtml+='</div></div>';
  });
  legend.innerHTML=legHtml;
}
calInitEdits();
renderMonthTabs();
renderDraftBanner();
renderCalendarGrid();
renderCalStats();
document.querySelectorAll("#cal-toolbar .fbtn").forEach(function(b){
  b.classList.toggle("active",b.dataset.mode===calDisplayMode);
});

document.getElementById("cal-toolbar")?.querySelectorAll(".fbtn").forEach(function(btn){
  btn.addEventListener("click",function(){
    calDisplayMode=btn.dataset.mode||"all";
    document.querySelectorAll("#cal-toolbar .fbtn").forEach(function(b){b.classList.toggle("active",b===btn);});
    renderCalendarGrid();
  });
});
const calSearch=document.getElementById("cal-search");
if(calSearch){
  calSearch.addEventListener("input",function(){
    calSearchQuery=calSearch.value.trim();
    renderCalendarGrid();
  });
}

const detail=document.getElementById("detail");
function closeSheet(){detail.style.display="none";}
detail.addEventListener("click",e=>{if(e.target===detail)closeSheet();});
document.addEventListener("keydown",e=>{
  if(e.key==="Escape"&&detail.style.display==="flex")closeSheet();
});
function openSheet(title,text,day,sub,status,desc,pricing){
  const tier=pricing||resolveItemPricing({name:text,status:status,desc:desc});
  let h='<div class="sheet"><button class="close">Close ✕</button>';
  h+='<h3>'+esc(title)+(sub?'  <span style="color:#8b96ad;font-size:12px;font-weight:600">· '+esc(sub)+'</span>':'')+(tier&&statusExpectsPricing(status,text)?pricingBadgeHtml(tier):"")+'</h3>';
  h+=buildOfferSheetHtml(text,status,desc,tier);
  const vd=VARIANT_DATES[title];
  if(vd&&vd.length){
    h+='<div class="datehdr">📅 Live on '+vd.length+' dates (May–Jul) · same-day context:</div><div class="datewrap">';
    vd.forEach(function(x){
      var tags='';
      if(x.sale)tags+='<span class="ctx s">Sale</span>';
      if(x.mgap)tags+='<span class="ctx m">MGAP · '+esc(x.mgap)+'</span>';
      if(!tags)tags='<span class="ctx n">No sale/MGAP</span>';
      h+='<div class="daterow"><span class="dt">'+esc(x.d.slice(5))+'</span>'+tags+'</div>';
    });
    h+='</div>';
  }
  h+='</div>';
  detail.innerHTML=h; detail.style.display="flex";
  detail.querySelector(".close").addEventListener("click",closeSheet);
}
const calGrid=document.getElementById("grid");
if(calGrid){
calGrid.addEventListener("click",function(e){
  const item=e.target.closest(".item");
  const days=MONTHS[currentMonthKey]||[];
  if(item){
    const day=days.find(function(d){return d.date==item.dataset.d;});
    const it=day.items[item.dataset.i];
    openSheet(cleanLabel(it.name),it.name,day,day.date+" · "+day.dow,it.status,it.desc,resolveItemPricing(it));
    return;
  }
  const srow=e.target.closest(".srow-click");
  if(srow){
    const day=days.find(function(d){return d.date==srow.dataset.d;});
    const s=day.seasons[srow.dataset.si];
    openSheet(cleanLabel(s.name),s.name,day,day.date+" · "+day.dow+" · "+(SEASON_ABBR[s.status]||s.status),s.status,s.desc);
    return;
  }
  const more=e.target.closest(".chead-open,.pred");
  if(more){
    const day=days.find(function(d){return String(d.date)===more.dataset.date;});
    if(day)openDaySheet(day);
  }
});
}
// ...
document.addEventListener("click",e=>{
  const row=e.target.closest("tr.click"); if(!row)return;
  const q=row.dataset.promo; if(!q)return;
  openSheet(q,q,null,"Offer contents");
});

// ---- tabs (deep-link: #cal, #health, #planner) ----
const DEFERRED_TABS=new Set(["revenue","economy","rel","guide","core","gems","offers"]);
const TAB_ALIASES={core:"economy",gems:"economy",offers:"guide"};
function showTab(id){
  id=TAB_ALIASES[id]||id;
  if(DEFERRED_TABS.has(id))id="cal";
  const tab=document.querySelector('.tab[data-tab="'+id+'"]');
  const panel=document.getElementById(id);
  if(!tab||!panel||!panel.classList.contains("panel"))return;
  document.querySelectorAll(".tab").forEach(x=>x.classList.toggle("active",x===tab));
  document.querySelectorAll("main .panel").forEach(x=>x.classList.toggle("active",x.id===id));
  const reco=document.querySelector(".reco-top");
  if(reco)reco.style.display=id==="cal"?"none":"";
  detail.style.display="none";
  window.scrollTo({top:0,behavior:"smooth"});
}
document.querySelectorAll(".tab").forEach(t=>{
  t.addEventListener("click",()=>{
    showTab(t.dataset.tab);
    history.replaceState(null,"","#"+t.dataset.tab);
  });
});
document.querySelectorAll("[data-jump-tab]").forEach(function(btn){
  btn.addEventListener("click",function(){
    const id=btn.dataset.jumpTab;
    if(!id)return;
    showTab(id);
    history.replaceState(null,"","#"+id);
  });
});
const hashTab=TAB_ALIASES[(location.hash||"#cal").replace("#","")]||(location.hash||"#cal").replace("#","");
if(document.getElementById(hashTab))showTab(hashTab);
else showTab("cal");
(function(){
  const reco=document.querySelector(".reco-top");
  if(reco&&(!location.hash||location.hash==="#cal"))reco.style.display="none";
})();
window.addEventListener("hashchange",()=>{
  const id=TAB_ALIASES[(location.hash||"#cal").replace("#","")]||(location.hash||"#cal").replace("#","");
  if(document.getElementById(id))showTab(id);
});

// ---- offers tab content ----
const OFFERS=[
  ["🛒","Buy All","2 denoms (currency+stamp base), buy both.",["Denom A: coin/red-stamp oriented slots","Denom B: gem/gold-stamp oriented slots","Extra reward slots must come from the real item/config"],"Both denoms get extra prizes beyond base."],
  ["🎭","Decoy / Bonanza","3 denoms — d1/d2 single base each, d3 bundle.",["Denom 1: one base direction + rewards","Denom 2: complementary base direction + rewards","Denom 3: combined base direction + optional on-top reward"],"Middle denom is the decoy."],
  ["🔁","Rolling Offer (Buy X Get Y)","Paid denom + free denoms by cycle/step.",["Purchase/base slot","SlotoBucks %, stamps, and reward-pool slots","Exact cycle rewards are shown only when written in the item/config"],"Any composition and order."],
  ["📉","Rolling More for Less","3 denoms tiered all-in-one, value rises d1<d2<d3.",["Base currency/stamp slots","SlotoBucks % slot","1-2 reward-pool slots per denom"],"Tiered pattern is common but exact content varies."],
  ["📅","Daily Deal (DD)","Coins + Gems + one central slot + pricing.",["Central slot: detected from item/config","Pricing controls generosity but exact amount is not inferred"],"Variants: Segmented / After Purchase / time windows."],
  ["🎁","RYD (Reveal Your Deal)","Coins + Gems + hook + RDS + %SB (rotating).",["Hook/reward is detected from item/config","Always needs value beyond SB alone"],"⛔ No 155% (one-time legacy value)."],
  ["🎉","Prize Mania","Prize bundle (free mix from pool).",["Bundle contents are detected from item/config","Do not assume the example mix from a different day"],"Composition varies by goal."],
];
const oc=document.getElementById("ocards");
OFFERS.forEach(([icon,t,st,denoms,tag])=>{
  let h='<h3><span class="ocard-icon">'+icon+'</span>'+t+'</h3><div class="struct">'+st+'</div>';
  denoms.forEach(d=>h+='<div class="denom">'+d+'</div>');
  h+='<div class="tagline">'+tag+'</div>';
  const e=document.createElement("div");e.className="ocard";e.innerHTML=h;oc.appendChild(e);
});

// ---- planning cards: Core coin sinks vs Gem planning surfaces ----
const COIN_PROMOS=[
  ["Core challenge → prize","Gameplay coin sink. Mechanics: Spin Zone / Win Master / PYP / Ace Loot / Spinner Clash / MES.","Prize content matters: Reg/Ace/Shiny/Wild/Dice/Hammers change engagement and burn. Gold remains purchase-slot only."],
  ["Custom Pod","Core coin-sink tool, 48 hours. X1000 regular · X1200 event · X1500 mega sale.","Day 1 standalone (daily coin sink)."],
  ["M.E.S / Tokens / Steps","Coin sink tied to event progress. Split by visible reward bucket in the Core table below.","Wild/Ace/Dice/Hammers versions should not be treated as the same mechanic."],
  ["PYP","Task-completion sink; player chooses path and burns through gameplay objectives.","Use harder prize content only when velocity/balance can absorb it."],
  ["Ace/Card Loot","Milestone ladder: wins/spins unlock card or ace rewards.","Stronger card tiers lift engagement, but should be planned as sink pressure, not revenue offer."],
  ["Clan/Dash","Dash points, badges and clan missions create sustained gameplay pressure.","Monday remains payer breadth day, but Core tab treats it as engagement/sink context."],
  ["Machine / Spin Zone / Win Master","Machine launch and challenge mechanics drive spin volume and coin burn.","Use together with the Core content table to see prize-specific composition."],
];
const GEM_PROMOS=[
  ["Short Term","Season layer that can create gem demand through short-window collection pressure.","Treat as planning surface; effect is directional and DOW-dominated in current CV."],
  ["Mid Term","Longer season layer; controls sustained gem pressure across multiple days.","Coordinate with album state rather than purchase-offer cadence."],
  ["Album","Album deadlines and card needs are the main gem-context driver.","Use for timing Shiny Show variants and avoiding overburn."],
  ["Shiny Show","Gem-spend mini-game; complete acts to send card value into album.","Variants matter: Joker / All Cards / Wild Guaranteed should be planned explicitly, not grouped blindly."],
];
function renderCards(list,elId){
  const c=document.getElementById(elId);
  list.forEach(([t,st,tag])=>{
    let h='<h3>'+t+'</h3><div class="struct">'+st+'</div>';
    if(tag)h+='<div class="tagline">'+tag+'</div>';
    const e=document.createElement("div");e.className="ocard";e.innerHTML=h;c.appendChild(e);
  });
}
renderCards(COIN_PROMOS,"pcards-coin");
renderCards(GEM_PROMOS,"pcards-gem");

// ==== Month Auto-Planner ====================================================
// Turns the guidelines you enter into a full-month draft calendar, entirely in
// the browser (no server, nothing sent anywhere). Deliberately mirrors the
// structural rules already enforced elsewhere in this codebase (weekday
// anchors, VFM exclusivity, MGAP/GGS/Dice/Shiny weekly caps, Rolling MFL
// cooldown, DD once/multiple, ADS+Core daily) — see .cursor/rules/
// mm_calendar_builder.mdc and mm_calendar/rules_cheatsheet.md for the full,
// authoritative rule set this simplifies. This is a v1 DRAFT assistant, same
// spirit as the existing manual chat-based process: it always shows its work
// and flags deviations rather than silently hiding them, and it never writes
// to Monday — review and edit here first.
//
// Predictions reuse the exact same forecast building blocks as the Calendar
// tab (promoEffect/pricingEffect/day-of-month curve/base DOW), so a promo
// placed here scores exactly like it would if it were real board content.
// The one thing that can't be reused is the month-specific "crowd" (user-base
// size) adjustment — an unstarted future month has no observed days yet — so
// that's an explicit, editable input instead of a hidden assumption.
const PL_STORAGE_PREFIX="mm_planner_v1_";
const PL_SHORT_TERM_ROT=["Blast","Battlesheep","SNL"];
const PL_MID_TERM_ROT=["Quest","Globez","Figz"];
const PL_ALBUM_PHASES=["Opening","Early","Mid","Late"];
const PL_WEEKDAY_PRIORITY=["Tue","Fri","Wed","Sun","Thu","Sat","Mon"];
// Card taxonomy — see mm_calendar/album_cards.md (the authoritative source; don't invent types
// or star ranges beyond what's documented there). Regular/Ace/Gold cards carry a 1★-5★ rarity;
// Gold is purchase-only (never a gameplay/Core reward); rarity climbs as the album nears closing
// ("תחילת אלבום = קלפים נמוכים, שבוע אחרון = שיא השימוש בקלפים"). Wild cards are a distinct,
// flexible currency with five sub-types of increasing reach/value (Ordinary < Gold ≈ Any <
// Supreme), not one generic "Wild" — see PL_WILD_TYPES.
const PL_STAR_BY_ALBUM_PHASE={Opening:{reg:2,ace:2,gold:3},Early:{reg:3,ace:3,gold:3},Mid:{reg:4,ace:4,gold:4},Late:{reg:5,ace:5,gold:5}};
const PL_WILD_TYPES=[
  {key:"wildOrdinary",name:"Wild Ordinary",need:"reg",value:2},
  {key:"wildAce",name:"Wild Ace",need:"ace",value:3},
  {key:"wildGold",name:"Wild Gold",need:"gold",value:4},
  {key:"wildAny",name:"Wild Any",need:"any",value:4},
  {key:"wildSupreme",name:"Wild Supreme",need:"wild",value:5},
];
const PL_DD_POOL=[
  {name:"DD- {WILD}",tiers:["wild"],once:true,cardType:"wild"},
  {name:"DD- SB Wheel up to 500%",tiers:[],once:false},
  {name:"DD- Hammers Wheel",tiers:[],once:false},
  {name:"DD- Bucks Wheel",tiers:[],once:false},
  {name:"DD- Dice Booster + 8 Hammers",tiers:[],once:false},
  {name:"DD- AS + 3 Parasheep",tiers:[],once:false},
  {name:"DD- {STARS}★ Reg card + Hammers",tiers:["reg"],once:false,cardType:"reg"},
  {name:"DD- {STARS}★ Ace card + SB Wheel",tiers:["ace"],once:false,cardType:"ace"},
  {name:"DD- {STARS}★ Gold card (on purchase) + AS",tiers:["gold"],once:false,cardType:"gold"},
  {name:"DD - Shiny Limited - Once",tiers:["shiny"],once:true,cardType:"shinyLimited"},
];
const PL_DD_MULTIPLE="DD- 100% SB + Hammers (multiple, replaces the once-per-player DD)";
const PL_SECOND_OFFER_POOL=["Buy All","RYD","Counter PO","Prize Mania","Decoy Bonanza"];
// Shiny Show variants: real board data names these Joker / All Cards / Wild Guaranteed / Crazy
// with Aces / Different Prizes. "Shiny Limited" is the priciest Shiny card in the game (purchase-
// only, no gameplay source) and per album_cards.md should show up ~once/week, not round-robin
// with the others — see plAssignCoreAdsAndBoosters, which forces exactly one Shiny Limited slot
// per week rather than picking it off this list by chance.
const PL_SHINY_VARIANTS=["Joker","All Cards","Wild Guaranteed","Crazy with Aces","Different Prizes"];
const PL_SHINY_LIMITED="Shiny Limited";
// Shiny Wolf: a mini-game (high-probability shot at a new Shiny card), per album_cards.md
// scheduled twice per Shiny Milestone/album phase — see plScheduleShinyWolf.
const PL_SHINY_WOLF="Shiny Despicable Wolf — mini-game (high-probability new Shiny card)";
const PL_CORE_POOL=[
  {name:"Core - PYP",cardType:"ace"},
  {name:"Core - Spinner Clash",cardType:null},
  {name:"Core - Ace Heist",cardType:"ace"},
  {name:"Core - Win Master",cardType:"reg"},
  {name:"MES - purchase to progress",cardType:null},
];
const PL_STATUS_OPTIONS=["Daily deal","Offers & coin sale","Rolling offer","Buy all","RYD","Counter PO","Prize Mania","MGAP","Gems","Core","Clan-Dash","ADS","Black Diamond"];
const PL_PRICING_OPTIONS=["","Medium","High","Max"];

function plDaysInMonth(y,m){return new Date(y,m,0).getDate();}
function plWeekday(y,m,d){return WEEKDAYS[new Date(Date.UTC(y,m-1,d)).getUTCDay()];}
function plIso(y,m,d){return y+"-"+String(m).padStart(2,"0")+"-"+String(d).padStart(2,"0");}
function plWeekIndex(dateNum){return Math.floor((dateNum-1)/7);}
function plMonthKey(y,m){return y+"-"+String(m).padStart(2,"0");}
function plItem(name,status,pricing,desc){return {name:name,status:status,pricing:pricing||null,desc:desc||"",backup:false,auto:true};}
function plDomBucket(dateNum){return dateNum<=2?"b1":dateNum<=7?"b2":dateNum<=14?"b3":dateNum<=21?"b4":dateNum<=28?"b5":"b6";}

// ---- generation ----
function plBuildSkeleton(cfg){
  const days=[];
  const n=plDaysInMonth(cfg.year,cfg.month);
  for(let d=1;d<=n;d++){
    days.push({date:d,dow:plWeekday(cfg.year,cfg.month,d),iso:plIso(cfg.year,cfg.month,d),tag:null,banner:null,sale:false,seasons:[],items:[],notes:""});
  }
  return days;
}
function plAssignSeasons(days,cfg){
  const stStart=Math.max(0,PL_SHORT_TERM_ROT.indexOf(cfg.shortTermStart));
  const mtStart=Math.max(0,PL_MID_TERM_ROT.indexOf(cfg.midTermStart));
  const albStart=Math.max(0,PL_ALBUM_PHASES.indexOf(cfg.albumPhase));
  days.forEach(function(day){
    const block=Math.floor((day.date-1)/5);
    day.seasons.push({name:PL_SHORT_TERM_ROT[(stStart+block)%3],status:"Short Term",desc:"5-day rotation, auto-planned"});
    day.seasons.push({name:PL_MID_TERM_ROT[(mtStart+block)%3],status:"Mid Term",desc:"Rotating Mid Term surface, auto-planned"});
    day.seasons.push({name:"Winovate",status:"Mid Term",desc:"8-9 day always-on cycle (simplified placeholder)"});
    day.seasons.push({name:"Mega Pods",status:"Mid Term",desc:"Mon-Mon always-on cycle (simplified placeholder)"});
    const weekIdx=Math.min(PL_ALBUM_PHASES.length-1,albStart+plWeekIndex(day.date));
    day._albumPhase=PL_ALBUM_PHASES[weekIdx];
    day.seasons.push({name:"Album — "+day._albumPhase+" phase",status:"Album",desc:"Phase advances weekly from configured start"});
  });
}
// ---- card bank / rarity / wild-type resolution (see album_cards.md) ----
function plCardBankAllows(entry,bank){
  bank=plNormalizeBankWeek(bank);
  if(!bank)return !entry.tiers.length;
  if(entry.cardType==="wild")return !!bank.wild&&plWildTypesAllowed(bank).length>0;
  if(entry.cardType==="shinyLimited")return !!bank.shiny&&!!bank.shinyLimited;
  return entry.tiers.every(function(t){return bank[t];});
}
function plWildVariant(bank,day,isFinalWeek){
  // Wild Supreme (any card, current OR prior albums — the single most flexible/valuable card in
  // the game) is reserved for the album's final push or a major event/machine day, never the
  // everyday default — matches "שבוע אחרון לסוף אלבום — Wildים בלבד" and the value ranking in
  // album_cards.md (Wild Supreme sits above every other wild sub-type).
  if((isFinalWeek||day.tag==="event"||day.tag==="machine")&&bank.wild)return PL_WILD_TYPES.find(function(w){return w.key==="wildSupreme";});
  const avail=PL_WILD_TYPES.filter(function(w){return w.need!=="wild"&&w.need!=="any"&&bank[w.need];});
  if(avail.length>=2){
    const anyAllowed=bank.wildAny&&PL_WILD_TYPES.find(function(w){return w.key==="wildAny";});
    if(anyAllowed)return anyAllowed;
    return avail.slice().sort(function(a,b){return b.value-a.value;})[0];
  }
  if(avail.length===1)return avail[0];
  return bank.wild?PL_WILD_TYPES.find(function(w){return w.key==="wildSupreme";}):null;
}
function plCardStars(cardType,phaseLabel){
  return (PL_STAR_BY_ALBUM_PHASE[phaseLabel]||PL_STAR_BY_ALBUM_PHASE.Mid)[cardType]||3;
}
const PL_BANK_WILD_COLS=[
  {bankKey:"wildOrd",wildKey:"wildOrdinary"},
  {bankKey:"wildAce",wildKey:"wildAce"},
  {bankKey:"wildGold",wildKey:"wildGold"},
  {bankKey:"wildAny",wildKey:"wildAny"},
  {bankKey:"wildSup",wildKey:"wildSupreme"},
];
const PL_BANK_DEFAULTS=[
  {reg:true,ace:false,gold:false,shiny:true,shinyLimited:true,wild:true,wildOrd:true,wildAce:false,wildGold:false,wildAny:false,wildSup:false},
  {reg:true,ace:true,gold:false,shiny:true,shinyLimited:true,wild:true,wildOrd:true,wildAce:true,wildGold:false,wildAny:true,wildSup:false},
  {reg:true,ace:true,gold:true,shiny:true,shinyLimited:true,wild:true,wildOrd:true,wildAce:true,wildGold:true,wildAny:true,wildSup:false},
  {reg:true,ace:true,gold:true,shiny:true,shinyLimited:true,wild:true,wildOrd:true,wildAce:true,wildGold:true,wildAny:true,wildSup:true},
];
function plNormalizeBankWeek(bank){
  const b=Object.assign({},PL_BANK_DEFAULTS[0],bank||{});
  if(b.wild===false){
    PL_BANK_WILD_COLS.forEach(function(c){b[c.bankKey]=false;});
  }
  if(b.wild&&!PL_BANK_WILD_COLS.some(function(c){return b[c.bankKey];})){
    if(b.reg)b.wildOrd=true;
    if(b.ace)b.wildAce=true;
    if(b.gold)b.wildGold=true;
    if(b.reg&&b.ace)b.wildAny=true;
  }
  if(b.shinyLimited===undefined)b.shinyLimited=!!b.shiny;
  return b;
}
function plWildTypesAllowed(bank){
  bank=plNormalizeBankWeek(bank);
  if(!bank.wild)return [];
  const out=[];
  PL_BANK_WILD_COLS.forEach(function(c){
    if(bank[c.bankKey]){
      const w=PL_WILD_TYPES.find(function(x){return x.key===c.wildKey;});
      if(w)out.push(w);
    }
  });
  return out;
}
function plPickWild(bank,day,isFinalWeek,seed){
  bank=plNormalizeBankWeek(bank);
  let allowed=plWildTypesAllowed(bank);
  if(!allowed.length){
    const v=plWildVariant(bank,day,isFinalWeek);
    return v||null;
  }
  if(isFinalWeek||day.tag==="event"||day.tag==="machine"){
    const sup=allowed.find(function(w){return w.key==="wildSupreme";});
    if(sup)return sup;
    allowed=allowed.slice().sort(function(a,b){return b.value-a.value;});
    return allowed[0];
  }
  const idx=Math.abs(seed||day.date)%allowed.length;
  return allowed[idx];
}
function plMaterializeDD(entry,ctx){
  // ctx: {bank, phaseLabel, isFinalWeek, day}
  if(entry.cardType==="wild"){
    const v=plPickWild(ctx.bank,ctx.day,ctx.isFinalWeek,ctx.day.date);
    if(!v){
      const reg=plCardStars("reg",ctx.phaseLabel);
      return {name:"DD- "+reg+"★ Reg card + Hammers Wheel",once:false,desc:"No wild sub-type in the weekly card bank — Reg DD instead (album_cards.md)."};
    }
    return {name:"DD- "+v.name,once:true,desc:"Wild sub-type: "+v.name+" (weekly bank only — never a type not checked in guidelines)."};
  }
  if(entry.cardType==="shinyLimited")return {name:entry.name,once:true,desc:"Priciest Shiny card in the game — purchase-only, ~once/week per album_cards.md."};
  if(entry.cardType){
    const stars=plCardStars(entry.cardType,ctx.phaseLabel);
    return {name:entry.name.replace("{STARS}",String(stars)),once:entry.once,desc:stars+"★ scaled to "+(ctx.phaseLabel||"Mid")+" album phase (rarity climbs as the album nears closing)."};
  }
  return {name:entry.name,once:entry.once,desc:""};
}
function plMaterializeCore(entry,phaseLabel,day){
  if(!entry.cardType)return entry.name;
  const stars=plCardStars(entry.cardType,phaseLabel);
  const st=day&&day.seasons?plShortTermSku(day):"Picks";
  if(/win master/i.test(entry.name)){
    return "Win Master — "+stars+"★ Reg card + "+st;
  }
  if(/ace heist/i.test(entry.name)){
    return "Ace Heist — "+stars+"★ Ace card";
  }
  return entry.name+" ("+stars+"★ "+(entry.cardType==="ace"?"Ace":"Reg")+")";
}
const PL_LBP_PROMOS=[
  "LBP — 30% Bigger Balls (Night Plan peak)",
  "LBP — 4 balls instead of 3 (Night Plan peak)",
  "LBP — 2 multiballs (Night Plan peak)",
  "LBP — all goldens + 20% bigger (Night Plan peak)",
  "LBP — Jackpot ball 150% + 4 balls (Night Plan peak)",
  "LBP — Jackpot ball 150% + 30% bigger (Night Plan peak)",
];
function plScheduleLbpPeaks(days){
  const peaks=days.filter(function(d){return d.dow==="Tue"||d.dow==="Sat";}).sort(function(a,b){return a.date-b.date;});
  peaks.forEach(function(day,idx){
    const window=day.dow==="Tue"?"Tue→Wed 00:00":"Sat→Sun 00:00";
    const hasLotto=day.items.some(function(i){return /lotto\s*[—-]\s*peak/i.test(i.name);});
    const hasLbp=day.items.some(function(i){return /^LBP\s*[—-]/i.test(i.name);});
    if(!hasLotto){
      day.items.push(plItem("Lotto — peak (Night Plan)","Offers & coin sale",null,"LBP peak night ("+window+") — paired with LBP promo"));
    }
    if(!hasLbp){
      day.items.push(plItem(PL_LBP_PROMOS[idx%PL_LBP_PROMOS.length],"Offers & coin sale",null,"Paired with Lotto peak same night ("+window+")"));
    }
  });
}
function plAssignWeekdayAnchors(days){
  days.forEach(function(day){
    if(day.dow==="Mon")day.items.push(plItem("Dash Pass — Dash Day","Core",null,"Recurring Monday anchor — avoid stacking another strong revenue promo today."));
    if(day.dow==="Thu")day.items.push(plItem("Golden Spin — weekly feature","Gems",null,"Recurring Thursday anchor (feature cadence, not primarily a revenue promo — historically a weak independent monetizer)."));
    if(day.dow==="Wed")day.items.push(plItem("Piggy — break for Coins","Offers & coin sale","High","Recurring Wednesday anchor; update the prize once decided."));
  });
}
function plAssignEventsAndMachines(days,cfg){
  cfg.events.forEach(function(ev){
    const day=days.find(function(d){return d.date===ev.date;});
    if(!day||day.tag)return;
    day.tag="event";day.banner=ev.banner;
    if(ev.major){
      day.sale=true;day._vfmUsed=true;day._eventFilled=true;
      day.items.push(plItem("Coin Sale — "+ev.banner,"Offers & coin sale","Max","Event ritual: flagship sale."));
      day.items.push(plItem("MGAP Bigger Multipliers — "+ev.banner+" themed","MGAP","High",""));
      day.items.push(plItem("Prize Mania — "+ev.banner,"Prize Mania","High",""));
      day.items.push(plItem("Happy Hour / Jumbo Giveaway","Offers & coin sale","High",""));
      day.items.push(plItem("Boosted Gemback","Gems",null,""));
      day.items.push(plItem("Custom Pod — "+ev.banner+" pack","Core",null,""));
    }else{
      day._eventFilled=true;
      day.items.push(plItem("Happy Hour — "+ev.banner,"Offers & coin sale","High",""));
    }
  });
  cfg.machineDates.forEach(function(dnum){
    const day=days.find(function(d){return d.date===dnum;});
    if(!day||day.tag)return;
    day.tag="machine";day.banner="Machine Launch";
    day.items.push(plItem("Machine Launch — Sneak Peek/Launch tie-in","Core",null,"Recurring machine-launch ritual."));
  });
}
function plAssignWeekendSale(days,cfg){
  if(!cfg.weekendSale)return;
  days.forEach(function(day){
    if(day.tag)return;
    if(day.dow==="Fri"||day.dow==="Sat"){
      day.sale=true;day._vfmUsed=true;
      day.items.push(plItem("Coin Sale","Offers & coin sale","High",""));
    }
  });
}
function plShortTermSku(day){
  const st=(day.seasons||[]).find(function(s){return s.status==="Short Term";});
  const n=((st&&st.name)||"").toLowerCase();
  if(n.includes("battlesheep"))return "2 Parasheep";
  if(n.includes("snl"))return "2 Dice";
  if(n.includes("blast"))return "Superboom";
  return "Picks";
}
function plMidTermBooster(day){
  const mt=(day.seasons||[]).find(function(s){
    return s.status==="Mid Term"&&s.name!=="Winovate"&&s.name!=="Mega Pods"&&!/winovate|mega pod/i.test(s.name||"");
  });
  const n=((mt&&mt.name)||"").toLowerCase();
  if(n.includes("globez"))return "3000 Hero Coins";
  if(n.includes("figz"))return "Figz Booster";
  return "Quest Booster";
}
function plBuildDecoyBonanzaItem(day,cfg,labelPrefix){
  const wk=plWeekIndex(day.date);
  const bank=plNormalizeBankWeek(cfg.cardBank[Math.min(3,wk)]||{});
  const nDays=plDaysInMonth(cfg.year,cfg.month);
  const isFinalWeek=wk>=Math.ceil(nDays/7)-1;
  const wild=plPickWild(bank,day,isFinalWeek,day.date*11);
  const stars={reg:plCardStars("reg",day._albumPhase),ace:plCardStars("ace",day._albumPhase),gold:plCardStars("gold",day._albumPhase)};
  const top=wild?wild.name:(bank.gold?(stars.gold+"★ Gold"):(bank.ace?(stars.ace+"★ Ace"):(stars.reg+"★ Reg")));
  const d1="Coins + 4 RDS + "+plShortTermSku(day);
  const d2="Gems + 1 GGS + "+plMidTermBooster(day);
  const d3="Coins + Gems + 4 RDS + 2 GGS + 3 Hammers + 100% SB + "+top;
  const prefix=labelPrefix||"Decoy Bonanza";
  const short=prefix+" — d3: "+top+" + bundle | H Pricing";
  const desc="d1 (coin+RDS base): "+d1+"\nd2 (gem+GGS base, decoy middle): "+d2+"\nd3 (bundle): "+d3;
  return plItem(short,"Offers & coin sale","High",desc);
}
function plBuildBuyAllItem(day,cfg){
  const bank=plNormalizeBankWeek(cfg.cardBank[Math.min(3,plWeekIndex(day.date))]||{});
  const stars={reg:plCardStars("reg",day._albumPhase),ace:plCardStars("ace",day._albumPhase),gold:plCardStars("gold",day._albumPhase)};
  const wild=plPickWild(bank,day,false,day.date);
  const st=plShortTermSku(day);
  const mt=plMidTermBooster(day);
  const coins=wild?("Coins + 4 RDS + "+wild.name):("Coins + 4 RDS + "+stars.reg+"★ Reg + "+st);
  const gems=bank.gold?("Gems + 1 GGS + "+stars.gold+"★ Gold + "+mt):("Gems + 1 GGS + "+stars.ace+"★ Ace + "+mt);
  const name="Buy All - Coins: "+coins+" | Gems: "+gems+" | H Pricing";
  const desc="Coins denom: "+coins+"\nGems denom: "+gems;
  return plItem(name,"Buy all","High",desc);
}
function plBuildSecondOffer(pick,day,cfg){
  const wk=plWeekIndex(day.date);
  const nDays=plDaysInMonth(cfg.year,cfg.month);
  const isFinalWeek=wk>=Math.ceil(nDays/7)-1;
  const bank=plNormalizeBankWeek(cfg.cardBank[Math.min(3,wk)]||{});
  const wild=plPickWild(bank,day,isFinalWeek,day.date+pick.length);
  const stars={reg:plCardStars("reg",day._albumPhase),ace:plCardStars("ace",day._albumPhase),gold:plCardStars("gold",day._albumPhase)};
  switch(pick){
    case "Buy All":
      return plBuildBuyAllItem(day,cfg);
    case "RYD":{
      const hook=wild?("Card Wheel (JP "+wild.name+") + 100% SB"):(bank.gold?(stars.gold+"★ Gold Card + 100% SB"):"100% SB + "+stars.reg+"★ Reg card");
      return plItem("RYD — "+hook,"RYD","High","");
    }
    case "Counter PO":return plItem("Counter PO — segmented topper","Counter PO","High","");
    case "Prize Mania":{
      const pm=wild?(wild.name+" | Dice Booster 6H | Coins, Gems"):(stars.reg+"★ Reg pack | Coins, Gems");
      return plItem("Prize Mania — "+pm,"Prize Mania","High","");
    }
    case "Decoy Bonanza":
      return plBuildDecoyBonanzaItem(day,cfg,"Decoy Bonanza");
    default:return plItem(pick,"Offers & coin sale","High","");
  }
}
function plScheduleSecondOffers(days,cfg){
  // Price Cut — monthly cap, spread roughly across the month
  let priceCutPlaced=0;
  const priceCutTargets=[Math.round(days.length*0.25),Math.round(days.length*0.72)];
  days.forEach(function(day){
    if(priceCutPlaced>=cfg.priceCutMonthly)return;
    if(day.tag||day._vfmUsed)return;
    if(priceCutTargets.includes(day.date)){
      day.items.push(plItem("Price Cut — 20% storewide","Offers & coin sale","High",""));
      day._vfmUsed=true;priceCutPlaced++;
    }
  });
  // MGAP — weekly cap, >=2 day spacing, never Monday/VFM day, exactly one BOGO/month
  const mgapWeek={};let lastMgapDate=-10;const bogo={done:false};
  days.forEach(function(day){
    if(day.tag||day._vfmUsed||day.dow==="Mon")return;
    const wk=plWeekIndex(day.date);
    mgapWeek[wk]=mgapWeek[wk]||0;
    if(mgapWeek[wk]>=cfg.mgapPerWeek)return;
    if(day.date-lastMgapDate<2)return;
    let variant="Bigger Multipliers";
    if(!bogo.done&&day.date>1&&day.date<days.length){variant="BOGO";bogo.done=true;}
    else if(mgapWeek[wk]%2===1)variant="Matched";
    day.items.push(plItem("MGAP "+variant,"MGAP","High",""));
    day._vfmUsed=true;mgapWeek[wk]++;lastMgapDate=day.date;
  });
  // Rolling More-for-Less — weekly cap 1 + cooldown
  let lastRolling=-Infinity;const rollingWeekUsed={};
  days.forEach(function(day){
    if(day.tag||day._vfmUsed||day.dow==="Mon")return;
    const wk=plWeekIndex(day.date);
    if(rollingWeekUsed[wk])return;
    if(day.date-lastRolling<cfg.rollingCooldown)return;
    day.items.push(plItem("Rolling Offer — Buy More for Less, 5 cycles","Rolling offer","High",""));
    day._vfmUsed=true;rollingWeekUsed[wk]=true;lastRolling=day.date;
  });
  // Extreme Stamp — weekly, never on a sale day
  const extremeWeekUsed={};
  days.forEach(function(day){
    if(day.tag||day._vfmUsed||day.sale)return;
    const wk=plWeekIndex(day.date);
    if(extremeWeekUsed[wk])return;
    day.items.push(plItem("Extreme Stamp — offers swap RDS for Extreme Stamp","Offers & coin sale","High",""));
    day._vfmUsed=true;day._noWildToday=true;extremeWeekUsed[wk]=true;
  });
  // Gems Sale — distinct monthly-capped track (not a VFM item)
  let gemsSalePlaced=0;
  const gemsTargets=[];
  if(cfg.gemsSalePerMonth>0){
    const step=Math.max(1,Math.floor(days.length/cfg.gemsSalePerMonth));
    for(let i=1;i<=cfg.gemsSalePerMonth;i++)gemsTargets.push(Math.min(days.length,i*step-1));
  }
  days.forEach(function(day){
    if(gemsSalePlaced>=cfg.gemsSalePerMonth||day.tag)return;
    if(gemsTargets.includes(day.date)){
      day.items.push(plItem("Gems Sale","Gems","High",""));
      gemsSalePlaced++;
    }
  });
  // Fill any day still missing a real second offer with a rotating pool (Buy All/RYD/Counter PO/Prize Mania/Decoy).
  // Prize Mania is FTD-oriented but still a "strong offer" name — keep it off Monday like the other revenue promos.
  let poolIdx=0;
  let lastSecondPick=null;
  days.forEach(function(day){
    if(day._eventFilled||day.dow==="Mon")return;
    const hasOffer=day.items.some(function(i){return /buy all|rolling|ryd|reveal your deal|counter po|prize mania|decoy|bonanza|coin sale|mgap|gems sale|price cut/i.test(i.name);});
    if(hasOffer)return;
    let tries=0,pick;
    do{
      pick=PL_SECOND_OFFER_POOL[poolIdx%PL_SECOND_OFFER_POOL.length];
      poolIdx++; tries++;
    }while((pick===lastSecondPick||(day.dow==="Mon"&&pick==="Prize Mania"))&&tries<PL_SECOND_OFFER_POOL.length*2);
    lastSecondPick=pick;
    day.items.push(plBuildSecondOffer(pick,day,cfg));
  });
}
function plWeekDays(days,weekIdx){return days.filter(function(d){return plWeekIndex(d.date)===weekIdx;});}
function plPlaceWeeklyCap(days,cap,filterFn,applyFn){
  if(cap<=0)return;
  const totalWeeks=Math.ceil(days.length/7);
  for(let w=0;w<totalWeeks;w++){
    const weekDays=plWeekDays(days,w);
    const ordered=PL_WEEKDAY_PRIORITY.map(function(dw){return weekDays.find(function(d){return d.dow===dw;});}).filter(Boolean);
    let placed=0;
    for(const day of ordered){
      if(placed>=cap)break;
      if(!filterFn(day))continue;
      applyFn(day);
      placed++;
    }
  }
}
function plAssignDailyDeal(days,cfg){
  let ddCounter=0,lastMax=false;
  const totalWeeks=Math.ceil(days.length/7);
  const shinyLimitedUsedWeek={};
  days.forEach(function(day){
    const wk=plWeekIndex(day.date);
    const bank=cfg.cardBank[Math.min(3,wk)]||{};
    const isFinalWeek=wk>=totalWeeks-1;
    let candidates=PL_DD_POOL.filter(function(c){return plCardBankAllows(c,bank);});
    if(day._noWildToday)candidates=candidates.filter(function(c){return c.cardType!=="wild";});
    if(shinyLimitedUsedWeek[wk])candidates=candidates.filter(function(c){return c.cardType!=="shinyLimited";});
    if(isFinalWeek&&bank.wild&&day._albumPhase==="Late"){
      const wildOnly=candidates.filter(function(c){return c.cardType==="wild"||!c.cardType;});
      if(wildOnly.length)candidates=wildOnly;
    }
    const pool=candidates.length?candidates:PL_DD_POOL.filter(function(c){return !c.tiers.length;});
    const entry=pool[ddCounter%pool.length];ddCounter++;
    const ctx={bank:bank,phaseLabel:day._albumPhase,isFinalWeek:isFinalWeek,day:day};
    const pick=plMaterializeDD(entry,ctx);
    if(entry.cardType==="shinyLimited")shinyLimitedUsedWeek[wk]=true;
    const pricing=(!lastMax&&(day.tag||day.sale))?"Max":"High";
    lastMax=pricing==="Max";
    day.items.push(plItem(pick.name,"Daily deal",pricing,pick.desc));
    if(pick.once)day.items.push(plItem(PL_DD_MULTIPLE,"Daily deal","High",""));
  });
}
function plGameplayCoreCount(day){
  return day.items.filter(function(i){
    const n=(i.name||"").toLowerCase();
    if(/shiny show|dash pass|golden spin|shiny wolf|album —/i.test(n))return false;
    return i.status==="Core"||/pyp|win master|ace heist|spinner|spin zone|mes|loot|machine launch|puzzle m/i.test(n);
  }).length;
}
function plMergeDailyDeals(day){
  const dds=day.items.filter(function(i){return i.status==="Daily deal";});
  if(dds.length!==2)return;
  const once=dds.find(function(i){return /once|wild|shiny limited/i.test(i.name)&&!/multiple/i.test(i.name);});
  const mult=dds.find(function(i){return /multiple|repeatable/i.test(i.name)||(once&&i!==once);});
  if(!once||!mult)return;
  once.name=once.name.replace(/\s*-\s*Once/i,"").replace(/\s*-\s*Once$/i,"")+" (Once + repeatable)";
  once.desc=(once.desc||"")+"\nRepeatable: "+mult.name;
  day.items=day.items.filter(function(i){return i!==mult;});
}
function plApplyDensityRules(days,cfg){
  if(!cfg.densityStandard)return;
  days.forEach(function(day){
    if(cfg.mergeDd)plMergeDailyDeals(day);
    if(cfg.noShinyMon&&day.dow==="Mon"){
      day.items=day.items.filter(function(i){return !/shiny show/i.test(i.name||"");});
    }
    while(plGameplayCoreCount(day)>1){
      let removed=false;
      for(let i=day.items.length-1;i>=0;i--){
        const it=day.items[i];
        const n=(it.name||"").toLowerCase();
        if(/shiny show|dash pass|puzzle m\.e\.s/i.test(n))continue;
        if(it.status==="Core"||/pyp|win master|ace heist|spinner|spin zone|mes|loot|machine launch/i.test(n)){
          day.items.splice(i,1);removed=true;break;
        }
      }
      if(!removed)break;
    }
  });
}
function plAssignCoreAdsAndBoosters(days,cfg){
  let coreCounter=0,adsCounter=0,shinyCounter=0;
  const shinyLimitedUsedWeek={};
  plPlaceWeeklyCap(days,cfg.shinyPerWeek,function(d){
    if(cfg.noShinyMon&&d.dow==="Mon")return false;
    const bank=plNormalizeBankWeek(cfg.cardBank[Math.min(3,plWeekIndex(d.date))]||{});
    return !!bank.shiny;
  },function(d){
    const wk=plWeekIndex(d.date);
    const bank=plNormalizeBankWeek(cfg.cardBank[Math.min(3,wk)]||{});
    if(cfg.shinyPerWeek>0&&bank.shinyLimited&&!shinyLimitedUsedWeek[wk]){
      shinyLimitedUsedWeek[wk]=true;
      d.items.push(plItem("Shiny Show — "+PL_SHINY_LIMITED,"Core",null,"Shiny Limited card — purchase-only, ~once/week (album_cards.md)."));
      return;
    }
    d.items.push(plItem("Shiny Show — "+PL_SHINY_VARIANTS[shinyCounter%PL_SHINY_VARIANTS.length],"Core",null,"Variant: Joker / All Cards / Wild Guaranteed / Crazy with Aces / Different Prizes."));
    shinyCounter++;
  });
  plPlaceWeeklyCap(days,cfg.ggsPerWeek,function(d){return !d._vfmUsed&&d.dow!=="Mon";},function(d){
    d.items.push(plItem("x2 GGS (3h window)","Gems",null,""));
  });
  plPlaceWeeklyCap(days,cfg.dicePerWeek,function(){return true;},function(d){
    d.items.push(plItem("Dice Booster 24h Purchase","Offers & coin sale",null,""));
  });
  plPlaceWeeklyCap(days,2,function(d){return d.dow!=="Mon";},function(d){
    d.items.push(plItem("Clan-Dash — mission set","Clan-Dash",null,""));
  });
  days.forEach(function(day){
    if(plGameplayCoreCount(day)<1){
      const entry=PL_CORE_POOL[coreCounter%PL_CORE_POOL.length];
      // Gold is purchase-only (never a gameplay reward — album_cards.md HARD rule), so Core pool
      // entries only ever resolve to reg/ace rarity, scaled to this day's album phase.
      day.items.push(plItem(plMaterializeCore(entry,day._albumPhase,day),"Core",null,entry.cardType?"Gameplay reward — Reg/Ace only, never Gold (HARD rule).":""));
      coreCounter++;
    }
    day.items.push(plAdsPrize(day,cfg,adsCounter));
    adsCounter++;
  });
}
function plAdsPrize(day,cfg,adsCounter){
  const bank=plNormalizeBankWeek(cfg.cardBank[Math.min(3,plWeekIndex(day.date))]||{});
  const phase=day._albumPhase;
  const slots=[["Coins","Low coins only — no high cards"],["Gems (low)","Low gems"],["Season pack (low)",""]];
  if(bank.reg){
    const s=Math.min(3,plCardStars("reg",phase));
    slots.push([s+"★ Reg card (low)","ADS max "+s+"★ Reg — no Gold/Ace/Wild/Shiny"]);
  }
  if(bank.ace){
    const s=Math.min(4,plCardStars("ace",phase));
    slots.push([s+"★ Ace card (low)","Gameplay Ace tier — still low-priority ADS"]);
  }
  const pick=slots[adsCounter%slots.length];
  return plItem("ADS PO — "+pick[0],"ADS",null,pick[1]);
}
function plCardTagHtml(name){
  const n=(name||"").toLowerCase();
  const tags=[];
  if(/shiny wolf/i.test(n))tags.push({c:"wolf",t:"Shiny Wolf"});
  else if(/shiny limited/i.test(n))tags.push({c:"shiny",t:"Shiny Limited"});
  else if(/shiny show/i.test(n)&&!/limited|wolf/i.test(n))tags.push({c:"shiny",t:"Shiny Show"});
  if(/wild supreme/i.test(n))tags.push({c:"wild",t:"Wild Supreme"});
  else if(/wild gold/i.test(n))tags.push({c:"wild",t:"Wild Gold"});
  else if(/wild any/i.test(n))tags.push({c:"wild",t:"Wild Any"});
  else if(/wild ace/i.test(n))tags.push({c:"wild",t:"Wild Ace"});
  else if(/wild ordinary/i.test(n))tags.push({c:"wild",t:"Wild Ordinary"});
  else if(/\bwild\b/i.test(n)&&!/wildcard/i.test(n))tags.push({c:"wild",t:"Wild"});
  const starM=n.match(/(\d)\s*★|★\s*(\d)|(\d)\s*\*\s*(reg|ace|gold)/i);
  if(starM)tags.push({c:"",t:(starM[1]||starM[2]||starM[3])+"★"});
  return tags.map(function(t){return '<span class="pdc-card-tag'+(t.c?" "+t.c:"")+'">'+esc(t.t)+'</span>';}).join("");
}
function plScheduleShinyWolf(days){
  // Twice per distinct Shiny Milestone/album phase (album_cards.md §"Shiny Wolf") — grouped by
  // the simplified 4-phase label the planner already tracks per day (day._albumPhase), not by
  // week, since a real Shiny Milestone spans ~3 weeks and this is a rare special mini-game, not
  // a weekly regular. Placed as a Core item so it stacks/validates like Shiny Show does, and it
  // already feeds the existing gem-consumption signal in predict() (searches for "shiny wolf").
  const byPhase={};
  days.forEach(function(d){(byPhase[d._albumPhase]=byPhase[d._albumPhase]||[]).push(d);});
  Object.keys(byPhase).forEach(function(phase){
    const candidates=byPhase[phase].filter(function(d){return d.dow!=="Mon"&&!d.tag;});
    const pool=candidates.length?candidates:byPhase[phase];
    const picks=[];
    if(pool.length){
      picks.push(pool[Math.floor(pool.length*0.25)]);
      if(pool.length>1)picks.push(pool[Math.min(pool.length-1,Math.floor(pool.length*0.75))]);
    }
    picks.forEach(function(d){
      if(d&&!d.items.some(function(i){return i.name===PL_SHINY_WOLF;})){
        d.items.push(plItem(PL_SHINY_WOLF,"Core",null,"Mini-game — 2x per album phase (album_cards.md)."));
      }
    });
  });
}
function plGenerate(cfg){
  const days=plBuildSkeleton(cfg);
  plAssignSeasons(days,cfg);
  plAssignWeekdayAnchors(days);
  plScheduleLbpPeaks(days);
  plAssignEventsAndMachines(days,cfg);
  plAssignWeekendSale(days,cfg);
  plScheduleSecondOffers(days,cfg);
  plAssignDailyDeal(days,cfg);
  plAssignCoreAdsAndBoosters(days,cfg);
  plScheduleShinyWolf(days);
  plApplyDensityRules(days,cfg);
  return days;
}

// ---- validation (ported subset of scripts/validate_calendar.py's HARD rules) ----
function plValidate(days,cfg){
  const V=[];
  function flag(d,msg){V.push("Day "+d+": "+msg);}
  const hammerWeek={},mgapWeek={},shinyWeek={},ggsWeek={},rmflDays=[];
  days.forEach(function(day){
    const d=day.date;
    const names=liveItems(day).map(function(i){return i.name;});
    const low=names.map(function(i){return i.toLowerCase();});
    const wk=plWeekIndex(d);
    if(day.sale&&day.dow!=="Fri"&&day.dow!=="Sat")flag(d,"Sale on "+day.dow+" (allowed Fri/Sat only)");
    const ham=names.filter(function(i){return /hammer/i.test(i)&&!/wheel/i.test(i);});
    if(ham.length>1)flag(d,"More than one Hammers source ("+ham.length+")");
    hammerWeek[wk]=(hammerWeek[wk]||0)+(ham.length?1:0);
    const vfm=low.filter(function(i){return /mgap|coins? sale|more.for.less|more for less|buy more|extreme stamp|price cut/.test(i);});
    if(vfm.length>1&&day.tag!=="event")flag(d,"More than one VFM: "+vfm.join(", "));
    if(low.some(function(i){return i.includes("clan pack");}))flag(d,"Clan Pack (banned)");
    if(day.dow==="Mon"&&low.some(function(i){return /mgap|coin sale|rolling|prize mania|buy all|ryd|decoy|bonanza/.test(i);}))flag(d,"Strong revenue promo on Monday (Dash Day)");
    const dds=low.filter(function(i){return i.startsWith("dd")||i.includes("daily deal");});
    if(!dds.length)flag(d,"Missing Daily Deal");
    const onceDd=dds.filter(function(i){return /wild|shiny limited/.test(i);});
    if(onceDd.length&&dds.length<2&&!names.some(function(n){return /once \+ repeatable/i.test(n);}))flag(d,"DD once (Wild/Shiny Limited) without alternate DD multiple");
    if(!low.some(function(i){return i.startsWith("ads");}))flag(d,"Missing ADS PO");
    if(day.dow==="Mon"){
      if(!low.some(function(i){return i.includes("dash pass")||i.includes("dash day");}))flag(d,"Monday without Dash Day");
    }else if(!low.some(function(i){return /core|mes|spin zone|pyp|win master|ace heist|spinner|loot|puzzle m/i.test(i);})){
      flag(d,"Missing Core (coin sink)");
    }
    if(cfg.densityStandard&&plGameplayCoreCount(day)>1)flag(d,"More than one gameplay Core ("+plGameplayCoreCount(day)+")");
    if(low.some(function(i){return i.includes("matched");})&&day.sale)flag(d,"MGAP Matched on Sale day (excluded)");
    if(low.some(function(i){return /more-for-less|more for less|buy more/.test(i);}))rmflDays.push(d);
    if(low.some(function(i){return i.includes("mgap");}))mgapWeek[wk]=(mgapWeek[wk]||0)+1;
    if(low.some(function(i){return i.includes("shiny show");}))shinyWeek[wk]=(shinyWeek[wk]||0)+1;
    if(low.some(function(i){return i.includes("ggs");}))ggsWeek[wk]=(ggsWeek[wk]||0)+1;
    if(day.dow==="Thu"&&!low.some(function(i){return i.includes("golden spin");}))flag(d,"Thursday without Golden Spin");
    if(low.some(function(i){return i.includes("extreme stamp");})&&day.sale&&day.tag!=="event")flag(d,"Extreme Stamp on Sale day");
    if(low.some(function(i){return i.includes("extreme stamp");})&&low.some(function(i){return i.includes("wild")&&!i.includes("shiny show");})&&day.tag!=="event")flag(d,"Extreme Stamp with Wild Card");
  });
  const lastDay=days.reduce(function(m,d){return Math.max(m,d.date);},0);
  function plDaysInWeekSlice(weekIdx){
    let n=0;
    for(let d=1;d<=lastDay;d++) if(plWeekIndex(d)===weekIdx)n++;
    return n;
  }
  Object.keys(mgapWeek).forEach(function(w){
    const c=mgapWeek[w];
    const wi=Number(w);
    if(c>cfg.mgapPerWeek)V.push("Week "+(wi+1)+": MGAP "+c+" (>"+cfg.mgapPerWeek+"/week)");
    else if(plDaysInWeekSlice(wi)>=4&&c<cfg.mgapPerWeek)V.push("Week "+(wi+1)+": MGAP "+c+" (<"+cfg.mgapPerWeek+"/week)");
    else if(plDaysInWeekSlice(wi)<4&&c<1)V.push("Week "+(wi+1)+": MGAP "+c+" (partial week needs ≥1)");
  });
  Object.keys(hammerWeek).forEach(function(w){if(hammerWeek[w]>cfg.hammersPerWeek)V.push("Week "+(Number(w)+1)+": Hammers "+hammerWeek[w]+" days (>"+cfg.hammersPerWeek+"/week)");});
  Object.keys(ggsWeek).forEach(function(w){if(ggsWeek[w]>cfg.ggsPerWeek)V.push("Week "+(Number(w)+1)+": x2 GGS "+ggsWeek[w]+" (>"+cfg.ggsPerWeek+"/week)");});
  Object.keys(shinyWeek).forEach(function(w){if(shinyWeek[w]>cfg.shinyPerWeek)V.push("Week "+(Number(w)+1)+": Shiny Show "+shinyWeek[w]+" (>"+cfg.shinyPerWeek+"/week)");});
  for(let i=1;i<rmflDays.length;i++){
    if(rmflDays[i]-rmflDays[i-1]<cfg.rollingCooldown)V.push("Rolling More for Less day "+rmflDays[i-1]+"→"+rmflDays[i]+": gap "+(rmflDays[i]-rmflDays[i-1])+"d (<"+cfg.rollingCooldown+"d cooldown)");
  }
  const shinyLtdWeek={}, wolfPhase={};
  days.forEach(function(day){
    const wk=plWeekIndex(day.date);
    const names=liveItems(day).map(function(i){return i.name.toLowerCase();});
    if(names.some(function(n){return /shiny limited/.test(n);}))shinyLtdWeek[wk]=(shinyLtdWeek[wk]||0)+1;
    if(names.some(function(n){return /shiny wolf/.test(n);}))wolfPhase[day._albumPhase]=(wolfPhase[day._albumPhase]||0)+1;
  });
  Object.keys(shinyLtdWeek).forEach(function(w){
    if(shinyLtdWeek[w]>2)V.push("Week "+(Number(w)+1)+": Shiny Limited appears "+shinyLtdWeek[w]+" times (target ≤2: DD once + Shiny Show once).");
  });
  Object.keys(wolfPhase).forEach(function(ph){
    if(wolfPhase[ph]!==2)V.push("Album phase "+ph+": Shiny Wolf placed "+wolfPhase[ph]+" times (target 2 per phase per album_cards.md).");
  });
  return V;
}

// ---- predictions (reuses promoEffect/pricingEffect/day-of-month curve — same model as Calendar) ----
function plPredictRevenue(day,prevDay,cfg){
  const BASE_DOW=(REV_CAL.base_dow&&Object.keys(REV_CAL.base_dow).length)?REV_CAL.base_dow:DEFAULT_BASE_DOW_REV;
  let rev=BASE_DOW[day.dow]||638;
  const why=["DOW base: $"+Math.round(BASE_DOW[day.dow])+"K","Planner crowd assumption "+(cfg.crowdK>=0?"+":"")+cfg.crowdK+"K/day (editable — no observed actuals yet for this month)"];
  rev+=cfg.crowdK;
  const domEntry=(REV_CAL.day_of_month_curve||{})[plDomBucket(day.date)];
  if(domEntry&&domEntry.value){rev+=domEntry.value;why.push("Day-of-month curve "+(domEntry.value>=0?"+":"")+domEntry.value+"K");}
  const eff=promoEffect(day);
  rev+=eff.bonus;why.push.apply(why,eff.why);
  const price=pricingEffect(day,REV_CAL,"K");
  if(price.value){rev+=price.value;why.push.apply(why,price.why);}
  if(prevDay){
    const prevEff=promoEffect(prevDay);
    const prevPrice=pricingEffect(prevDay,REV_CAL,"K");
    const carry=Math.round((prevEff.bonus+prevPrice.value)*CARRYOVER_FRACTION);
    if(carry){rev+=carry;why.push("Carryover from "+prevDay.dow+" "+prevDay.date+" "+(carry>=0?"+":"")+carry+"K");}
    const prevIsBrandedEvent=prevDay.items.some(function(i){return /carnival|\bdays? event\b|festival/i.test(i.name);});
    if(prevDay.sale&&!prevDay.tag&&!prevIsBrandedEvent){rev+=ABSORPTION_PENALTY;why.push("Post-sale absorption "+ABSORPTION_PENALTY+"K");}
  }
  rev=Math.max(400,Math.min(1300,Math.round(rev)));
  return {rev:rev,why:why};
}
function plPredictPU(day,cfg){
  const BASE_DOW=(PU_CAL.base_dow&&Object.keys(PU_CAL.base_dow).length)?PU_CAL.base_dow:DEFAULT_BASE_DOW_PU;
  let pu=BASE_DOW[day.dow]||27096;
  const why=["DOW base: "+Math.round(BASE_DOW[day.dow])+" PU","Planner crowd assumption "+(cfg.crowdPu>=0?"+":"")+cfg.crowdPu+"% (editable)"];
  pu+=pu*cfg.crowdPu/100;
  const it=liveItems(day).map(function(x){return x.name.toLowerCase();});
  const has=r=>it.some(i=>r.test(i));
  const mgapText=it.filter(function(t){return t.includes("mgap");}).join(" | ");
  let pct=0;const pbMap=PU_CAL.promo_bonus||{};
  function addPu(key,label){const e=pbMap[key];if(!e)return;pct+=e.value;why.push(label+" "+(e.value>=0?"+":"")+e.value.toFixed(2)+"% PU");}
  if(has(/custom pod/))addPu("customPod","Custom Pod");
  if(has(/coins? sale/))addPu("coinSale","Coin Sale");
  if(/bogo/.test(mgapText))addPu("mgapBogo","MGAP BOGO");
  if(has(/buy all/))addPu("buyAll","Buy All");
  if(has(/golden spin/))addPu("goldenSpin","Golden Spin");
  if(has(/prize mania/))addPu("prizeMania","Prize Mania");
  if(has(/counter po/))addPu("counterPo","Counter PO");
  if(has(/rolling/))addPu("rolling","Rolling");
  const pricePu=pricingEffect(day,PU_CAL,"%");
  if(pricePu.value){pct+=pricePu.value;why.push.apply(why,pricePu.why);}
  if(pct)pu+=pu*pct/100;
  pu=Math.max(15000,Math.min(40000,Math.round(pu)));
  return {pu:pu,why:why};
}

// ---- state, rendering, editing ----
let PL_STATE=null,PL_EDIT_DATE=null;
function plStateKey(monthKey){return PL_STORAGE_PREFIX+monthKey;}
function plSaveState(){
  if(!PL_STATE)return;
  try{
    const days=PL_STATE.days.map(function(d){return {date:d.date,dow:d.dow,iso:d.iso,tag:d.tag,banner:d.banner,sale:d.sale,seasons:d.seasons,items:d.items,notes:d.notes};});
    localStorage.setItem(plStateKey(PL_STATE.cfg.monthKey),JSON.stringify({cfg:PL_STATE.cfg,days:days}));
    const st=document.getElementById("pl-status");
    if(st)st.textContent="Saved locally (this browser) "+new Date().toLocaleTimeString();
  }catch(e){/* localStorage unavailable/full — non-fatal, draft still works this session */}
}
function plLoadState(monthKey){
  try{const raw=localStorage.getItem(plStateKey(monthKey));return raw?JSON.parse(raw):null;}catch(e){return null;}
}
function plComputeAll(days,cfg){
  let prev=null;
  days.forEach(function(day){
    const r=plPredictRevenue(day,prev,cfg);
    const p=plPredictPU(day,cfg);
    day._pred={rev:r.rev,revWhy:r.why,pu:p.pu,puWhy:p.why};
    prev=day;
  });
}
function plRenderSummary(days){
  const el=document.getElementById("pl-summary");if(!el)return;
  const totalRev=days.reduce(function(s,d){return s+d._pred.rev;},0);
  const avgPu=Math.round(days.reduce(function(s,d){return s+d._pred.pu;},0)/days.length);
  const eventDays=days.filter(function(d){return d.tag==="event";}).length;
  const itemCount=days.reduce(function(s,d){return s+liveItems(d).length;},0);
  el.innerHTML=[
    ["Forecast month revenue","$"+(totalRev/1000).toFixed(2)+"M"],
    ["Avg predicted PU/day",avgPu.toLocaleString()],
    ["Event/holiday days",String(eventDays)],
    ["Avg items/day",(itemCount/days.length).toFixed(1)],
  ].map(function(kv){return '<div class="kpi"><div class="v">'+kv[1]+'</div><div class="l">'+kv[0]+'</div></div>';}).join("");
}
function plRenderViolations(V){
  const el=document.getElementById("pl-violations");if(!el)return;
  el.classList.toggle("has-issues",V.length>0);
  if(!V.length){
    el.innerHTML='<div class="pv-title">✅ No HARD-rule violations detected in this draft.</div><div>Still review SOFT deviations (frequency targets, variety, pricing balance, prize selection) manually before approving — this generator intentionally simplifies the full rule set in mm_calendar_builder.mdc.</div>';
    return;
  }
  el.innerHTML='<div class="pv-title">⚠️ '+V.length+' check(s) need attention</div><ul>'+V.map(function(v){return "<li>"+esc(v)+"</li>";}).join("")+'</ul>';
}
function plRenderDays(days){
  const el=document.getElementById("pl-days");if(!el)return;
  el.innerHTML="";
  days.forEach(function(day){
    const card=document.createElement("div");
    card.className="plan-day-card"+(day.tag==="event"?" is-event":"")+(day.tag==="machine"?" is-machine":"");
    const seasonLine=day.seasons&&day.seasons.length?'<div class="pdc-banner" style="color:var(--mut)">'+day.seasons.slice(0,2).map(function(s){return esc(s.name);}).join(" · ")+'</div>':"";
    const chips=liveItems(day).filter(function(i){
      if(PL_STATE&&PL_STATE.cfg&&PL_STATE.cfg.hideAdsChips&&i.status==="ADS")return false;
      return true;
    }).map(function(i){
      const lbl=cleanLabel(i.name);
      return '<span class="pdc-item'+(i.status==="ADS"?" tag-ads":"")+'" title="'+esc(compactOfferDescription(i.desc||""))+'">'+esc(lbl)+(i.pricing?" · "+i.pricing:"")+plCardTagHtml(i.name)+'</span>';
    }).join("");
    card.innerHTML=
      '<div class="pdc-date"><span class="dow">'+day.dow+'</span><span class="num">'+day.date+'</span></div>'+
      '<div class="pdc-items">'+(day.banner?'<div class="pdc-banner">'+esc(day.banner)+'</div>':"")+seasonLine+chips+'</div>'+
      '<div class="pdc-pred"><div class="rev">$'+Math.round(day._pred.rev)+'K</div><span class="pu">'+Math.round(day._pred.pu/1000)+'K PU</span></div>';
    card.addEventListener("click",function(){plOpenEditor(day.date);});
    el.appendChild(card);
  });
}
function plAfterPlanChange(){
  plComputeAll(PL_STATE.days,PL_STATE.cfg);
  plRenderSummary(PL_STATE.days);
  plRenderViolations(plValidate(PL_STATE.days,PL_STATE.cfg));
  plRenderDays(PL_STATE.days);
  if(PL_EDIT_DATE!=null){const d=plCurrentDay();if(d)plRenderEditorPred(d);}
  plSaveState();
}
function plCurrentDay(){
  if(!PL_STATE||PL_EDIT_DATE==null)return null;
  return PL_STATE.days.find(function(d){return d.date===PL_EDIT_DATE;});
}
function plOpenEditor(dateNum){
  PL_EDIT_DATE=dateNum;
  plRenderEditor();
  document.getElementById("pl-editor").classList.remove("hidden");
}
function plCloseEditor(){
  document.getElementById("pl-editor").classList.add("hidden");
  PL_EDIT_DATE=null;
}
function plRenderEditorPred(day){
  const idx=PL_STATE.days.indexOf(day);
  const prev=idx>0?PL_STATE.days[idx-1]:null;
  const r=plPredictRevenue(day,prev,PL_STATE.cfg);
  const p=plPredictPU(day,PL_STATE.cfg);
  day._pred={rev:r.rev,revWhy:r.why,pu:p.pu,puWhy:p.why};
  const el=document.getElementById("pl-editor-pred");if(!el)return;
  el.innerHTML='<b>Live prediction:</b> $'+Math.round(r.rev)+'K · '+Math.round(p.pu).toLocaleString()+' PU';
}
function plRenderEditor(){
  const day=plCurrentDay();
  const wrap=document.getElementById("pl-editor");
  if(!day){wrap.classList.add("hidden");return;}
  const itemsHtml=day.items.map(function(item,idx){
    return '<div class="plan-item-row" data-idx="'+idx+'">'+
      '<input type="text" data-field="name" value="'+esc(item.name)+'" title="'+esc(item.desc||"")+'"/>'+
      '<select data-field="status">'+PL_STATUS_OPTIONS.map(function(s){return '<option'+(s===item.status?" selected":"")+'>'+s+'</option>';}).join("")+'</select>'+
      '<select data-field="pricing">'+PL_PRICING_OPTIONS.map(function(p){return '<option value="'+p+'"'+((item.pricing||"")===p?" selected":"")+'>'+(p||"—")+'</option>';}).join("")+'</select>'+
      '<button type="button" data-remove="'+idx+'" title="Remove">✕</button>'+
      (item.userEdited?'<span class="edited-tag edited-tag-inline">EDITED</span>':"")+
      (item.desc?'<div class="pl-item-why">'+esc(compactOfferDescription(item.desc))+'</div>':"")+
    '</div>';
  }).join("");
  wrap.innerHTML=
    '<div class="plan-editor-panel">'+
      '<div class="plan-editor-head"><h3>'+day.dow+' '+day.date+(day.banner?" · "+esc(day.banner):"")+'</h3><button type="button" class="pl-btn ghost" id="pl-editor-close">Close</button></div>'+
      itemsHtml+
      '<div class="plan-editor-add">'+
        '<input type="text" id="pl-new-item-name" placeholder="New item name"/>'+
        '<select id="pl-new-item-status">'+PL_STATUS_OPTIONS.map(function(s){return "<option>"+s+"</option>";}).join("")+'</select>'+
        '<select id="pl-new-item-pricing">'+PL_PRICING_OPTIONS.map(function(p){return '<option value="'+p+'">'+(p||"—")+'</option>';}).join("")+'</select>'+
        '<button type="button" class="pl-btn" id="pl-add-item">+ Add</button>'+
      '</div>'+
      '<label class="pl-field">Notes for this day (place for changes / rationale)<textarea id="pl-day-notes">'+esc(day.notes||"")+'</textarea></label>'+
      '<div class="plan-editor-pred" id="pl-editor-pred"></div>'+
      '<div class="pl-actions" style="margin-top:12px"><button type="button" class="pl-btn ghost" id="pl-regenerate-day">↻ Regenerate this day (keeps anchors, rerolls offers)</button></div>'+
    '</div>';
  plRenderEditorPred(day);
  wrap.querySelectorAll(".plan-item-row").forEach(function(row){
    row.querySelectorAll("input,select").forEach(function(inp){
      inp.addEventListener("change",function(){
        const it=day.items[Number(row.dataset.idx)];
        it[inp.dataset.field]=inp.value;
        it.userEdited=true;
        plAfterPlanChange();
      });
    });
  });
  wrap.querySelectorAll("[data-remove]").forEach(function(btn){
    btn.addEventListener("click",function(){
      day.items.splice(Number(btn.dataset.remove),1);
      plRenderEditor();plAfterPlanChange();
    });
  });
  document.getElementById("pl-add-item").addEventListener("click",function(){
    const name=document.getElementById("pl-new-item-name").value.trim();
    if(!name)return;
    day.items.push(plItem(name,document.getElementById("pl-new-item-status").value,document.getElementById("pl-new-item-pricing").value||null,""));
    day.items[day.items.length-1].userEdited=true;
    plRenderEditor();plAfterPlanChange();
  });
  document.getElementById("pl-day-notes").addEventListener("input",function(e){day.notes=e.target.value;plSaveState();});
  document.getElementById("pl-editor-close").addEventListener("click",plCloseEditor);
  document.getElementById("pl-regenerate-day").addEventListener("click",function(){plRegenerateDay(day.date);});
}
function plRegenerateDay(dateNum){
  const day=PL_STATE.days.find(function(d){return d.date===dateNum;});
  if(!day||!PL_STATE)return;
  const cfg=PL_STATE.cfg;
  day._rerollSeed=(day._rerollSeed||0)+1;
  day.items=[];
  plAssignWeekdayAnchors([day]);
  if(day.tag==="event"||day.tag==="machine"){
    day.notes=(day.notes?day.notes+" · ":"")+"Event/machine ritual isn't quick-rerolled — edit items directly or clear the tag and regenerate the full month.";
  }
  if(day.sale)day.items.push(plItem("Coin Sale","Offers & coin sale","High",""));
  const wk=plWeekIndex(day.date);
  const totalWeeks=Math.ceil(PL_STATE.days.length/7);
  const bank=cfg.cardBank[Math.min(3,wk)]||{};
  let candidates=PL_DD_POOL.filter(function(c){return plCardBankAllows(c,bank);});
  if(day._noWildToday)candidates=candidates.filter(function(c){return c.cardType!=="wild";});
  const pool=candidates.length?candidates:PL_DD_POOL.filter(function(c){return !c.tiers.length;});
  const entry=pool[(day.date+day._rerollSeed)%pool.length];
  const pick=plMaterializeDD(entry,{bank:bank,phaseLabel:day._albumPhase,isFinalWeek:wk>=totalWeeks-1,day:day});
  day.items.push(plItem(pick.name,"Daily deal","High",pick.desc));
  if(pick.once)day.items.push(plItem(PL_DD_MULTIPLE,"Daily deal","High",""));
  if(!day.sale&&day.dow!=="Mon"){
    const pick2=PL_SECOND_OFFER_POOL[(day.date+day._rerollSeed)%PL_SECOND_OFFER_POOL.length];
    day.items.push(plBuildSecondOffer(pick2,day,cfg));
  }
  plApplyDensityRules([day],PL_STATE?PL_STATE.cfg:{densityStandard:true,mergeDd:true,noShinyMon:true});
  const coreEntry=PL_CORE_POOL[(day.date+day._rerollSeed)%PL_CORE_POOL.length];
  day.items.push(plItem(plMaterializeCore(coreEntry,day._albumPhase,day),"Core",null,""));
  day.items.push(plItem("ADS PO — Coins (low prize only)","ADS",null,""));
  plRenderEditor();
  plAfterPlanChange();
}

// ---- export ----
function plExportJSON(){
  if(!PL_STATE)return;
  const blob=new Blob([JSON.stringify({cfg:PL_STATE.cfg,days:PL_STATE.days},null,1)],{type:"application/json"});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob);
  a.download="mm_plan_"+PL_STATE.cfg.monthKey+".json";
  a.click();
}
function plFallbackCopy(text){
  const ta=document.createElement("textarea");ta.value=text;document.body.appendChild(ta);ta.select();
  try{document.execCommand("copy");}catch(e){/* clipboard API unavailable in this context */}
  document.body.removeChild(ta);
  const st=document.getElementById("pl-status");if(st)st.textContent="Copied to clipboard.";
}
function plExportTSV(){
  if(!PL_STATE)return;
  const lines=["Date\tDOW\tBanner\tItems\tPricing\tPredicted Revenue ($K)\tPredicted PU"];
  PL_STATE.days.forEach(function(day){
    const items=liveItems(day).map(function(i){return i.name;}).join(" | ");
    const pricing=liveItems(day).map(function(i){return i.pricing||"";}).filter(Boolean).join(" | ");
    lines.push([day.date,day.dow,day.banner||"",items,pricing,Math.round(day._pred.rev),Math.round(day._pred.pu)].join("\t"));
  });
  const text=lines.join("\n");
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(function(){
      const st=document.getElementById("pl-status");if(st)st.textContent="Copied "+PL_STATE.days.length+" days to clipboard — paste into Sheets/Excel.";
    }).catch(function(){plFallbackCopy(text);});
  }else plFallbackCopy(text);
}

// ---- form wiring ----
function plNextMonthDefault(){
  const today=CAL_META.today||"2026-07-01";
  let y=Number(today.slice(0,4)),m=Number(today.slice(5,7))+1;
  if(m>12){m=1;y++;}
  return {year:y,month:m};
}
function plDefaultCrowdGuess(){
  const cur=CAL_META.current_month;
  const rk=(REV_CAL.crowd_adj_by_month||{})[cur]||0;
  const pk=(PU_CAL.crowd_adj_by_month||{})[cur]||0;
  return {crowdK:Math.round(rk),crowdPu:Math.round(pk*10)/10};
}
function plPopulateBankTable(){
  const tbody=document.querySelector("#pl-bank-table tbody");
  if(!tbody)return;
  tbody.innerHTML="";
  const cols=["reg","ace","gold","shiny","shinyLimited","wild","wildOrd","wildAce","wildGold","wildAny","wildSup"];
  for(let w=0;w<4;w++){
    const d=PL_BANK_DEFAULTS[w];
    const tr=document.createElement("tr");
    tr.innerHTML='<td>Week '+(w+1)+'</td>'+cols.map(function(k){
      return '<td><input type="checkbox" id="pl-bank-'+w+'-'+k+'"'+(d[k]?" checked":"")+'/></td>';
    }).join("");
    tbody.appendChild(tr);
  }
  plUpdateBankPhaseHint();
}
function plUpdateBankPhaseHint(){
  const phaseEl=document.getElementById("pl-album-phase");
  const el=document.getElementById("pl-bank-phase-hint");
  if(!el||!phaseEl)return;
  const phase=phaseEl.value||"Mid";
  const s=PL_STAR_BY_ALBUM_PHASE[phase]||PL_STAR_BY_ALBUM_PHASE.Mid;
  el.textContent="At month start (“"+phase+"” phase), generated Reg/Ace/Gold use "+s.reg+"★ / "+s.ace+"★ / "+s.gold+"★ (Gold = purchase-only). Each calendar week bumps album phase — rarity climbs toward Late. Wild prizes use explicit sub-types (Ordinary / Ace / Gold / Any / Supreme), not a generic “wild card”.";
}
function plReadCardBank(){
  const bank=[];
  const cols=["reg","ace","gold","shiny","shinyLimited","wild","wildOrd","wildAce","wildGold","wildAny","wildSup"];
  for(let w=0;w<4;w++){
    const row={};
    cols.forEach(function(k){
      const el=document.getElementById("pl-bank-"+w+"-"+k);
      row[k]=el?el.checked:false;
    });
    bank.push(plNormalizeBankWeek(row));
  }
  return bank;
}
function plParseEvents(){
  const text=document.getElementById("pl-events").value||"";
  const events=[];
  text.split("\n").forEach(function(line){
    const m=line.match(/^\s*(\d{1,2})\s*:\s*(.+?)\s*$/);
    if(!m)return;
    const date=Number(m[1]);
    let banner=m[2];
    const major=/\[major\]/i.test(banner);
    banner=banner.replace(/\[major\]/i,"").trim();
    if(date>=1&&banner)events.push({date:date,banner:banner,major:major});
  });
  return events;
}
function plParseMachineDates(){
  const text=document.getElementById("pl-machine-dates").value||"";
  return text.split(",").map(function(s){return Number(s.trim());}).filter(function(n){return n>=1&&n<=31;});
}
function plReadConfig(){
  const year=Number(document.getElementById("pl-year").value)||plNextMonthDefault().year;
  const month=Number(document.getElementById("pl-month").value)||plNextMonthDefault().month;
  return {
    year:year,month:month,monthKey:plMonthKey(year,month),
    weekendSale:document.getElementById("pl-weekend-sale").checked,
    hammersPerWeek:Number(document.getElementById("pl-hammers-week").value)||0,
    mgapPerWeek:Number(document.getElementById("pl-mgap-week").value)||0,
    ggsPerWeek:Number(document.getElementById("pl-ggs-week").value)||0,
    dicePerWeek:Number(document.getElementById("pl-dice-week").value)||0,
    shinyPerWeek:Number(document.getElementById("pl-shiny-week").value)||0,
    gemsSalePerMonth:Number(document.getElementById("pl-gemsale-month").value)||0,
    priceCutMonthly:Number(document.getElementById("pl-pricecut-month").value)||0,
    machineCount:Number(document.getElementById("pl-machine-count").value)||0,
    rollingCooldown:Number(document.getElementById("pl-rolling-cooldown").value)||10,
    shortTermStart:document.getElementById("pl-shortterm-start").value,
    midTermStart:document.getElementById("pl-midterm-start").value,
    albumPhase:document.getElementById("pl-album-phase").value,
    cardBank:plReadCardBank(),
    events:plParseEvents(),
    machineDates:plParseMachineDates(),
    eventsRaw:document.getElementById("pl-events").value,
    machineDatesRaw:document.getElementById("pl-machine-dates").value,
    crowdK:Number(document.getElementById("pl-crowd-k").value)||0,
    crowdPu:Number(document.getElementById("pl-crowd-pu").value)||0,
    notes:document.getElementById("pl-notes").value||"",
    densityStandard:document.getElementById("pl-density-standard")?document.getElementById("pl-density-standard").checked:true,
    noShinyMon:document.getElementById("pl-no-shiny-mon")?document.getElementById("pl-no-shiny-mon").checked:true,
    noSecondMon:document.getElementById("pl-no-second-mon")?document.getElementById("pl-no-second-mon").checked:true,
    mergeDd:document.getElementById("pl-merge-dd")?document.getElementById("pl-merge-dd").checked:true,
    hideAdsChips:document.getElementById("pl-hide-ads-chips")?document.getElementById("pl-hide-ads-chips").checked:true,
  };
}
function plWriteConfig(cfg){
  document.getElementById("pl-year").value=cfg.year;
  document.getElementById("pl-month").value=cfg.month;
  document.getElementById("pl-weekend-sale").checked=cfg.weekendSale;
  document.getElementById("pl-hammers-week").value=cfg.hammersPerWeek;
  document.getElementById("pl-mgap-week").value=cfg.mgapPerWeek;
  document.getElementById("pl-ggs-week").value=cfg.ggsPerWeek;
  document.getElementById("pl-dice-week").value=cfg.dicePerWeek;
  document.getElementById("pl-shiny-week").value=cfg.shinyPerWeek;
  document.getElementById("pl-gemsale-month").value=cfg.gemsSalePerMonth;
  document.getElementById("pl-pricecut-month").value=cfg.priceCutMonthly;
  document.getElementById("pl-machine-count").value=cfg.machineCount;
  document.getElementById("pl-rolling-cooldown").value=cfg.rollingCooldown;
  document.getElementById("pl-shortterm-start").value=cfg.shortTermStart;
  document.getElementById("pl-midterm-start").value=cfg.midTermStart;
  document.getElementById("pl-album-phase").value=cfg.albumPhase;
  document.getElementById("pl-crowd-k").value=cfg.crowdK;
  document.getElementById("pl-crowd-pu").value=cfg.crowdPu;
  document.getElementById("pl-notes").value=cfg.notes||"";
  if(document.getElementById("pl-density-standard"))document.getElementById("pl-density-standard").checked=cfg.densityStandard!==false;
  if(document.getElementById("pl-no-shiny-mon"))document.getElementById("pl-no-shiny-mon").checked=cfg.noShinyMon!==false;
  if(document.getElementById("pl-no-second-mon"))document.getElementById("pl-no-second-mon").checked=cfg.noSecondMon!==false;
  if(document.getElementById("pl-merge-dd"))document.getElementById("pl-merge-dd").checked=cfg.mergeDd!==false;
  if(document.getElementById("pl-hide-ads-chips"))document.getElementById("pl-hide-ads-chips").checked=cfg.hideAdsChips!==false;
  document.getElementById("pl-events").value=cfg.eventsRaw||"";
  document.getElementById("pl-machine-dates").value=cfg.machineDatesRaw||"";
  (cfg.cardBank||[]).forEach(function(bank,w){
    const b=plNormalizeBankWeek(bank);
    ["reg","ace","gold","shiny","shinyLimited","wild","wildOrd","wildAce","wildGold","wildAny","wildSup"].forEach(function(k){
      const el=document.getElementById("pl-bank-"+w+"-"+k);
      if(el)el.checked=!!b[k];
    });
  });
  plUpdateBankPhaseHint();
}
function plOnGenerate(){
  const cfg=plReadConfig();
  const days=plGenerate(cfg);
  PL_STATE={cfg:cfg,days:days};
  plAfterPlanChange();
  const st=document.getElementById("pl-status");
  if(st)st.textContent="Generated draft for "+cfg.monthKey+" — review every day before using it.";
}
function plOnReset(){
  const cfg=plReadConfig();
  localStorage.removeItem(plStateKey(cfg.monthKey));
  PL_STATE=null;
  ["pl-summary","pl-violations","pl-days"].forEach(function(id){const el=document.getElementById(id);if(el)el.innerHTML="";});
  const st=document.getElementById("pl-status");
  if(st)st.textContent="Cleared saved draft for "+cfg.monthKey+".";
}
function plLoadForMonth(y,m){
  const monthKey=plMonthKey(y,m);
  const saved=plLoadState(monthKey);
  const st=document.getElementById("pl-status");
  if(saved){
    plWriteConfig(saved.cfg);
    PL_STATE={cfg:saved.cfg,days:saved.days};
    plAfterPlanChange();
    if(st)st.textContent="Loaded saved draft for "+monthKey+".";
  }else{
    PL_STATE=null;
    ["pl-summary","pl-violations","pl-days"].forEach(function(id){const el=document.getElementById(id);if(el)el.innerHTML="";});
    if(st)st.textContent="No saved draft for "+monthKey+" yet — fill in guidelines and generate one.";
  }
}
function plInitForm(){
  if(!document.getElementById("pl-form"))return;
  const def=plNextMonthDefault();
  document.getElementById("pl-year").value=def.year;
  document.getElementById("pl-month").value=def.month;
  plPopulateBankTable();
  const guess=plDefaultCrowdGuess();
  document.getElementById("pl-crowd-k").value=guess.crowdK;
  document.getElementById("pl-crowd-pu").value=guess.crowdPu;
  document.getElementById("pl-generate").addEventListener("click",plOnGenerate);
  document.getElementById("pl-reset").addEventListener("click",plOnReset);
  document.getElementById("pl-export-json").addEventListener("click",plExportJSON);
  document.getElementById("pl-export-tsv").addEventListener("click",plExportTSV);
  ["pl-year","pl-month"].forEach(function(id){
    document.getElementById(id).addEventListener("change",function(){
      plLoadForMonth(Number(document.getElementById("pl-year").value),Number(document.getElementById("pl-month").value));
    });
  });
  const phaseEl=document.getElementById("pl-album-phase");
  if(phaseEl)phaseEl.addEventListener("change",plUpdateBankPhaseHint);
  plLoadForMonth(def.year,def.month);
}
plInitForm();
