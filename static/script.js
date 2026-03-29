// password strength + crack-time estimator
(function(){
  const pw = document.getElementById('password');
  if(!pw) return;

  const fill = document.getElementById('strength-fill');
  const levelText = document.getElementById('strength-level');
  const crackEst = document.getElementById('crack-est');

  const chkLength = document.getElementById('chk-length');
  const chkUpper = document.getElementById('chk-upper');
  const chkNumber = document.getElementById('chk-number');
  const chkSpecial = document.getElementById('chk-special');

  // guesses per second estimate (conservative high-power attacker)
  const GUESSES_PER_SEC = 1e9; // 1 billion guesses/sec

  function charsetSize(p){
    let size = 0;
    if(/[a-z]/.test(p)) size += 26;
    if(/[A-Z]/.test(p)) size += 26;
    if(/[0-9]/.test(p)) size += 10;
    if(/[^A-Za-z0-9]/.test(p)) size += 32; // treat symbols approx
    return size;
  }

  function bitsOfEntropy(len, charset){
    if(charset <= 1) return 0;
    return Math.log2(Math.pow(charset, len));
  }

  function secsToReadable(s){
    if(!isFinite(s)) return '∞';
    if(s < 1) return (s*1000).toFixed(2) + ' ms';
    const mins = s/60;
    if(mins < 1) return s.toFixed(2) + ' sec';
    const hours = mins/60;
    if(hours < 24) return hours.toFixed(2) + ' hours';
    const days = hours/24;
    if(days < 365) return days.toFixed(2) + ' days';
    const years = days/365;
    if(years < 1000) return years.toFixed(2) + ' years';
    return (years/1000).toFixed(2) + 'k years';
  }

  function classifyByTime(seconds){
    // thresholds: <1 day Weak, 1 day-1 year Medium, >=1 year Strong
    const days = seconds / (60*60*24);
    if(seconds === Infinity) return 'Very Strong';
    if(days < 1) return 'Weak';
    if(days < 365) return 'Medium';
    return 'Strong';
  }

  function updateUI(){
    const p = pw.value || '';
    // check items
    chkLength.style.opacity = (p.length >= 8) ? 1 : 0.4;
    chkUpper.style.opacity = (/[A-Z]/.test(p)) ? 1 : 0.4;
    chkNumber.style.opacity = (/\d/.test(p)) ? 1 : 0.4;
    chkSpecial.style.opacity = (/[^A-Za-z0-9]/.test(p)) ? 1 : 0.4;

    if(p.length === 0){
      fill.style.width = '0%';
      levelText.innerText = '—';
      crackEst.innerText = '—';
      return;
    }

    const cs = charsetSize(p);
    const bits = bitsOfEntropy(p.length, cs);
    // approximate guesses = 2^(bits-1) (average)
    const guesses = Math.pow(2, Math.max(0, bits-1));
    let seconds = guesses / GUESSES_PER_SEC;
    if(guesses === 0) seconds = Infinity;

    const level = classifyByTime(seconds);

    // set bar width (0-100) from bits (cap at 80 bits)
    const maxBits = 80;
    const pct = Math.min(100, Math.round((bits / maxBits)*100));
    fill.style.width = pct + '%';

    // color by level
    if(level === 'Weak'){
      fill.style.background = '#ff4d4f';
    } else if(level === 'Medium'){
      fill.style.background = '#ffd666';
    } else {
      fill.style.background = '#2ecc71';
    }

    levelText.innerText = level;
    crackEst.innerText = secsToReadable(seconds);
  }

  pw.addEventListener('input', updateUI);
  // initial
  updateUI();
})();