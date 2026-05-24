/* Lexi-Koh quiz engine — vanilla JS */

let questions = [];
let currentIndex = 0;
let correctCount = 0;
let answers = [];
let listId = null;
const OPTION_LABELS = ['A', 'B', 'C', 'D'];

function initQuiz(id) {
  listId = id;
  questions = JSON.parse(document.getElementById('questionsData').textContent);
  showQuestion(0);
}

/* ── Show a question ─────────────────────────────────────── */
function showQuestion(index) {
  const q = questions[index];
  const total = questions.length;

  document.getElementById('progressText').textContent =
    `Pregunta ${index + 1} de ${total}`;
  document.getElementById('progressBar').style.width =
    `${(index / total) * 100}%`;
  document.getElementById('quizWord').textContent = q.english;
  document.getElementById('scoreCounter').textContent =
    `${correctCount} correcta${correctCount !== 1 ? 's' : ''}`;

  const feedbackEl = document.getElementById('feedbackMsg');
  feedbackEl.classList.add('d-none');
  feedbackEl.textContent = '';

  document.getElementById('nextBtn').classList.add('d-none');

  // Build option buttons
  const container = document.getElementById('optionsContainer');
  container.innerHTML = '';
  q.options.forEach((option, i) => {
    const btn = document.createElement('button');
    btn.className = 'quiz-option';
    btn.type = 'button';
    btn.dataset.answer = option;
    btn.innerHTML =
      `<span class="quiz-label">${OPTION_LABELS[i]}</span>${option}`;
    btn.addEventListener('click', () => selectAnswer(option, q, btn));
    container.appendChild(btn);
  });
}

/* ── Handle answer selection ─────────────────────────────── */
function selectAnswer(chosen, question, clickedBtn) {
  const isCorrect = chosen === question.correct;
  const allBtns = document.querySelectorAll('.quiz-option');

  // Disable all buttons and reveal correct answer
  allBtns.forEach(btn => {
    btn.disabled = true;
    if (btn.dataset.answer === question.correct) {
      btn.classList.add('correct');
    }
  });

  if (!isCorrect) {
    clickedBtn.classList.add('wrong');
  } else {
    correctCount++;
    document.getElementById('scoreCounter').textContent =
      `${correctCount} correcta${correctCount !== 1 ? 's' : ''}`;
  }

  // Inline feedback message
  const feedbackEl = document.getElementById('feedbackMsg');
  feedbackEl.classList.remove('d-none');
  if (isCorrect) {
    feedbackEl.style.color = '#1A4A32';
    feedbackEl.textContent = randomPositive();
  } else {
    feedbackEl.style.color = '#6B1A3A';
    feedbackEl.textContent = `La respuesta es: ${question.correct}`;
  }

  answers.push({ word_id: question.word_id, chosen, correct: isCorrect });

  const nextBtn = document.getElementById('nextBtn');
  nextBtn.classList.remove('d-none');
  if (currentIndex >= questions.length - 1) {
    nextBtn.innerHTML = 'Ver resultados <i class="bi bi-trophy ms-1"></i>';
  } else {
    nextBtn.innerHTML = 'Siguiente <i class="bi bi-arrow-right ms-1"></i>';
  }
}

/* ── Advance to next question or submit ──────────────────── */
function nextQuestion() {
  currentIndex++;
  if (currentIndex < questions.length) {
    showQuestion(currentIndex);
  } else {
    submitQuiz();
  }
}

/* ── Send answers to server ──────────────────────────────── */
async function submitQuiz() {
  // Hide quiz, update progress bar to 100%
  document.getElementById('progressBar').style.width = '100%';
  document.getElementById('quizSection').classList.add('d-none');

  try {
    const res = await fetch(`/quiz/${listId}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    });
    if (!res.ok) throw new Error('Server error');
    const results = await res.json();
    showResults(results);
  } catch (err) {
    // Fallback: show local results without server data
    showResults({
      total: answers.length,
      correct: correctCount,
      percentage: Math.round((correctCount / answers.length) * 100),
      wrong_words: [],
      newly_mastered: [],
      list_mastered: false,
    });
  }
}

/* ── Render results screen ───────────────────────────────── */
function showResults(results) {
  const section = document.getElementById('resultsSection');
  section.classList.remove('d-none');
  section.scrollIntoView({ behavior: 'smooth' });

  const pct = results.percentage ?? 0;
  document.getElementById('scoreCircle').textContent = `${pct}%`;
  document.getElementById('scoreText').textContent =
    `${results.correct} de ${results.total} correctas`;
  document.getElementById('motivationalMsg').textContent = motivationalMessage(pct);

  // List mastered banner
  if (results.list_mastered) {
    document.getElementById('listMasteredBanner').classList.remove('d-none');
    const ctaBtn = document.getElementById('ctaBtn');
    ctaBtn.innerHTML = '&#127942; ¡Lista dominada! Practicar de nuevo';
  }

  // Newly mastered words
  if (results.newly_mastered && results.newly_mastered.length > 0) {
    const sec = document.getElementById('masteredSection');
    sec.classList.remove('d-none');
    const list = document.getElementById('masteredList');
    results.newly_mastered.forEach(w => {
      const span = document.createElement('span');
      span.className = 'lk-chip';
      span.style.cssText =
        'background:rgba(184,237,212,.35);color:#1A4A32;font-weight:600;';
      span.textContent = `${w.english} → ${w.spanish}`;
      list.appendChild(span);
    });
  }

  // Words to review
  if (results.wrong_words && results.wrong_words.length > 0) {
    const sec = document.getElementById('reviewSection');
    sec.classList.remove('d-none');
    const list = document.getElementById('reviewList');
    results.wrong_words.forEach(w => {
      const div = document.createElement('div');
      div.className = 'lk-word-card d-flex justify-content-between align-items-center';
      div.innerHTML =
        `<span class="fw-semibold">${w.english}</span>
         <span class="text-muted small">${w.spanish}</span>`;
      list.appendChild(div);
    });
  }
}

/* ── Helpers ─────────────────────────────────────────────── */
function motivationalMessage(pct) {
  if (pct === 100) return '¡Perfecto! ¡Eres increíble! 🌟';
  if (pct >= 80)  return '¡Muy bien! Sigue así.';
  if (pct >= 60)  return '¡Buen trabajo! Puedes mejorar.';
  if (pct >= 40)  return '¡Sigue practicando, vas por buen camino!';
  return '¡No te rindas! La práctica hace al maestro.';
}

const POSITIVE_MSGS = [
  '¡Correcto!', '¡Muy bien!', '¡Exacto!', '¡Perfecto!', '¡Así se hace!'
];
function randomPositive() {
  return POSITIVE_MSGS[Math.floor(Math.random() * POSITIVE_MSGS.length)];
}
