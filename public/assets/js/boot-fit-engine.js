// Vital4 Boot Fit Engine — educational boot-sizing + fit guidance
// Logic reflects general ski-boot fitting practice; not a substitute for a certified bootfitter.
(function () {
  var form = document.getElementById('bff');
  var results = document.getElementById('results');
  if (!form || !results) return;

  var inputs = {};
  // segmented button groups
  document.querySelectorAll('[data-seg]').forEach(function (group) {
    var key = group.getAttribute('data-seg');
    group.querySelectorAll('button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        group.querySelectorAll('button').forEach(function (b) {
          b.setAttribute('aria-pressed', 'false');
        });
        btn.setAttribute('aria-pressed', 'true');
        inputs[key] = btn.getAttribute('data-value');
      });
    });
  });

  var sizingRadios = document.querySelectorAll('input[name="sizing"]');
  var sizingGroups = {
    us: document.getElementById('grp-us'),
    mondo: document.getElementById('grp-mondo'),
    footlength: document.getElementById('grp-footlength'),
  };
  sizingRadios.forEach(function (r) {
    r.addEventListener('change', function () {
      Object.keys(sizingGroups).forEach(function (k) {
        sizingGroups[k].hidden = k !== r.value;
      });
    });
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    compute();
  });

  function roundHalf(n) {
    return Math.round(n * 2) / 2;
  }

  function getMondo() {
    var method = form.querySelector('input[name="sizing"]:checked').value;
    if (method === 'us') {
      var us = parseFloat(document.getElementById('us-size').value);
      var gender = inputs.gender || 'm';
      if (!us || us < 4 || us > 16) return null;
      return roundHalf(us + (gender === 'w' ? 16.5 : 18));
    }
    if (method === 'footlength') {
      var cm = parseFloat(document.getElementById('foot-length').value);
      if (!cm || cm < 18 || cm > 36) return null;
      return roundHalf(cm + 1.0); // ~1 cm of shell room beyond foot length
    }
    var m = parseFloat(document.getElementById('mondo-size').value);
    if (!m || m < 18 || m > 36) return null;
    return roundHalf(m);
  }

  function lastBand() {
    var w = inputs.forefoot || 'average';
    var map = {
      narrow: { label: 'Narrow', range: '92–98 mm', score: 0 },
      average: { label: 'Medium', range: '98–102 mm', score: 1 },
      wide: { label: 'Wide', range: '102–106 mm', score: 2 },
      xwide: { label: 'Extra-wide', range: '106–112 mm', score: 3 },
    };
    return map[w] || map.average;
  }

  function volumeClass() {
    var lb = lastBand();
    var instep = inputs.instep || 'average';
    var instepScore = instep === 'low' ? 0 : instep === 'high' ? 2 : 1;
    var total = lb.score + instepScore;
    if (total <= 1) return { label: 'Low volume', note: 'Race / performance fit — snug, responsive.' };
    if (total >= 4) return { label: 'High volume', note: 'Comfort / freeride fit — roomier, more forgiving.' };
    return { label: 'Medium volume', note: 'Balanced fit — the most common starting point.' };
  }

  function flexRange() {
    var ability = inputs.ability || 'intermediate';
    var weight = parseFloat(document.getElementById('weight').value) || 160;
    var base = {
      beginner: [50, 70],
      intermediate: [70, 90],
      advanced: [90, 110],
      expert: [110, 130],
    }[ability] || [70, 90];
    var lo = base[0],
      hi = base[1];
    if (weight >= 190) {
      lo += 10;
      hi += 10;
    } else if (weight <= 140) {
      lo -= 10;
      hi -= 10;
    }
    if (lo < 50) lo = 50;
    if (hi > 140) hi = 140;
    return lo + '–' + hi;
  }

  function brandFit(vol) {
    var matrix = {
      low: [
        { brand: 'Tecnica', note: 'Mach1 LV — narrow, low-volume performance lasts.' },
        { brand: 'Lange', note: 'RX/LX LV — low-volume, race-heritage fit.' },
      ],
      medium: [
        { brand: 'Salomon', note: 'S/Pro — medium, anatomical fit with a snug instep.' },
        { brand: 'Atomic', note: 'Hawx — medium volume, adaptable last.' },
        { brand: 'Nordica', note: 'Speedmachine — medium-volume, progressive flex.' },
      ],
      high: [
        { brand: 'Head', note: 'Kore — wide, high-volume, lightweight.' },
        { brand: 'Dalbello', note: 'Panterra — wide, high-volume, strong freeride line.' },
        { brand: 'Fischer', note: 'RC4/Transalp — wide options across race and tour.' },
        { brand: 'K2', note: 'Recon — wide, high-volume, forgiving.' },
      ],
    };
    return matrix[vol] || matrix.medium;
  }

  function terrainNote() {
    var t = inputs.terrain || 'allmountain';
    return (
      {
        piste: 'Frontside/piste: lean toward a lower-volume, stiffer boot for edge precision.',
        allmountain: 'All-mountain: a medium-volume, medium-flex boot covers the widest range.',
        powder: 'Freeride/powder: more volume and a slightly softer flex add forgiveness in soft snow.',
        touring: 'Backcountry touring: prioritize a lighter boot with a walk mode and a rockered (GripWalk/touring) sole — verify binding compatibility.',
      }[t] || ''
    );
  }

  function usFromMondo(mondo, gender) {
    return gender === 'w' ? roundHalf(mondo - 16.5) : roundHalf(mondo - 18);
  }

  function compute() {
    var mondo = getMondo();
    if (!mondo) {
      results.hidden = false;
      results.innerHTML =
        '<div class="result-card"><p class="result-card__note">Enter a valid size to compute a fit.</p></div>';
      return;
    }
    var gender = inputs.gender || 'm';
    var lb = lastBand();
    var vol = volumeClass();
    var flex = flexRange();
    var volKey = vol.label.toLowerCase().split(' ')[0]; // 'low' | 'medium' | 'high'
    var brands = brandFit(volKey);

    var chips = brands
      .map(function (b) {
        return '<span class="brand-chip">' + b.brand + '</span>';
      })
      .join('');
    var brandNotes = brands
      .map(function (b) {
        return '<li><strong>' + b.brand + '</strong> — ' + b.note + '</li>';
      })
      .join('');

    results.hidden = false;
    results.innerHTML =
      '<div class="grid grid--2">' +
      resultCard('Mondo (shell) size', mondo.toFixed(1) + ' cm', 'Shell length. Aim for ~1–2 cm of space behind your heel in a shell fit (liner out).') +
      resultCard('US size', 'Men\u2019s ' + usFromMondo(mondo, 'm') + ' / Women\u2019s ' + usFromMondo(mondo, 'w'), 'Approximate — mondo is the sizing standard, US is a convenience.') +
      '</div>' +
      '<div class="grid grid--2">' +
      resultCard('Last width', lb.label + ' — ' + lb.range, 'Forefoot/last width. Narrow lasts suit slim feet; wide lasts suit broad forefeet.') +
      resultCard('Volume class', vol.label, vol.note) +
      '</div>' +
      '<div class="result-card">' +
      '<div class="result-card__label">Flex index range</div>' +
      '<div class="result-card__value">' + flex + '</div>' +
      '<p class="result-card__note">Flex is NOT standardized across brands — a 100 in one brand differs from another. Use this as a starting band, adjusted for your ' + (parseFloat(document.getElementById('weight').value) || 160) + ' lb frame and ' + (inputs.ability || 'intermediate') + ' ability. ' + terrainNote() + '</p>' +
      '</div>' +
      '<div class="result-card">' +
      '<div class="result-card__label">Brands that tend to fit this profile</div>' +
      '<div style="margin-top:var(--space-3)">' + chips + '</div>' +
      '<ul style="margin-top:var(--space-4);padding-left:var(--space-5)">' + brandNotes + '</ul>' +
      '<p class="result-card__note">General fit tendencies only — lasts vary by model year. Always try the actual boot on; a shop bootfitter can shell-fit and punch/stretch for your foot.</p>' +
      '</div>' +
      '<div class="result-card">' +
      '<div class="result-card__label">Verify at the shop</div>' +
      '<ul style="margin-top:var(--space-3);padding-left:var(--space-5)">' +
      '<li>Shell fit: remove the liner, slide your foot in, check for 1–2 cm behind the heel.</li>' +
      '<li>Forefoot: no pressure points across the widest part when buckled.</li>' +
      '<li>Ankle lock: heel stays down when you flex forward into the tongue.</li>' +
      '<li>Sole type: confirm alpine / GripWalk / touring sole matches your bindings.</li>' +
      '</ul></div>' +
      '<div class="disclaimer"><strong>Educational guidance only.</strong> This tool estimates sizing and fit from general practice. It does not set binding release values and does not replace a certified bootfitter or shop technician. Have final fit and binding setup confirmed by a professional.</div>';
  }

  function resultCard(label, value, note) {
    return (
      '<div class="result-card"><div class="result-card__label">' +
      label +
      '</div><div class="result-card__value">' +
      value +
      '</div>' +
      (note ? '<p class="result-card__note">' + note + '</p>' : '') +
      '</div>'
    );
  }

  // trigger default segmented selections
  document.querySelectorAll('[data-seg]').forEach(function (group) {
    var first = group.querySelector('button[aria-pressed="true"]') || group.querySelector('button');
    if (first) first.click();
  });
})();
