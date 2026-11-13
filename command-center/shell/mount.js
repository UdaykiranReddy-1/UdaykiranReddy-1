/**
 * @typedef {import('../compose/composer.js').MorningLayoutPlan} MorningLayoutPlan
 * @typedef {import('../domain/document.js').ReminderId} ReminderId
 */

/**
 * @typedef {{
 *   onDayNote?: (note: string) => void;
 *   onAddReminder?: (text: string) => void;
 *   onToggleReminder?: (id: ReminderId) => void;
 *   onFocusChange?: (priority: string) => void;
 * }} MountHandlers
 */

/** @type {MountHandlers | null} */
let handlers = null;

/**
 * @param {MountHandlers} h
 */
export function setMountHandlers(h) {
  handlers = h;
}

/**
 * @param {HTMLElement} root
 */
export function clearSlots(root) {
  for (const slot of root.querySelectorAll(".panel-slot")) {
    slot.replaceChildren();
  }
}

/**
 * @param {MorningLayoutPlan} plan
 * @param {HTMLElement} root
 */
export function mountLayoutPlan(plan, root) {
  for (const slot of plan.slots) {
    const el = document.getElementById(slot.slotId);
    if (!el) continue;
    el.replaceChildren();
    const title = document.createElement("h2");
    title.textContent = slot.title;
    el.appendChild(title);
    const body = document.createElement("div");
    body.className = "panel-body";
    el.appendChild(body);
    renderPayload(body, slot.payload);
  }
}

/**
 * @param {HTMLElement} body
 * @param {import('../compose/registry.js').PanelPayload} payload
 */
function renderPayload(body, payload) {
  switch (payload.kind) {
    case "today":
      renderToday(body, payload);
      break;
    case "schedule":
      renderSchedule(body, payload);
      break;
    case "reminders":
      renderReminders(body, payload);
      break;
    case "commute":
      renderCommute(body, payload);
      break;
    case "quick-links":
      renderQuickLinks(body, payload);
      break;
    case "focus":
      renderFocus(body, payload);
      break;
    default:
      body.textContent = "Unknown panel";
  }
}

/**
 * @param {HTMLElement} body
 * @param {{ dateLabel: string; weather: object | null; dayNote: string }} p
 */
function renderToday(body, p) {
  const date = document.createElement("p");
  date.className = "date-label";
  date.textContent = p.dateLabel;
  body.appendChild(date);

  if (p.weather) {
    const w = document.createElement("div");
    w.className = "weather-block";
    w.innerHTML = `<span>${escapeHtml(p.weather.summary)}</span><span class="muted">${p.weather.tempC}°C · ${escapeHtml(p.weather.locationLabel)}</span>`;
    body.appendChild(w);
  } else {
    const hint = document.createElement("p");
    hint.className = "muted";
    hint.textContent = "Loading weather…";
    body.appendChild(hint);
  }

  const note = document.createElement("input");
  note.type = "text";
  note.className = "day-note-input";
  note.placeholder = "One-line note for today";
  note.value = p.dayNote;
  note.addEventListener("change", () => handlers?.onDayNote?.(note.value));
  note.addEventListener("blur", () => handlers?.onDayNote?.(note.value));
  body.appendChild(note);
}

/**
 * @param {HTMLElement} body
 * @param {{ nextEvents: { title: string; timeLabel: string }[] }} p
 */
function renderSchedule(body, p) {
  if (p.nextEvents.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-hint";
    empty.textContent = "No events on the calendar.";
    body.appendChild(empty);
    return;
  }
  const ul = document.createElement("ul");
  ul.className = "event-list";
  for (const ev of p.nextEvents) {
    const li = document.createElement("li");
    li.className = "event-item";
    li.innerHTML = `<span>${escapeHtml(ev.title)}</span><span class="time-label">${escapeHtml(ev.timeLabel)}</span>`;
    ul.appendChild(li);
  }
  body.appendChild(ul);
}

/**
 * @param {HTMLElement} body
 * @param {{ dueToday: { id: ReminderId; text: string }[]; canQuickAdd: boolean }} p
 */
function renderReminders(body, p) {
  const ul = document.createElement("ul");
  ul.className = "reminder-list";
  if (p.dueToday.length === 0) {
    const li = document.createElement("li");
    li.className = "empty-hint";
    li.textContent = "Nothing due today.";
    ul.appendChild(li);
  } else {
    for (const r of p.dueToday) {
      const li = document.createElement("li");
      li.className = "reminder-item";
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn-ghost";
      btn.textContent = "✓";
      btn.title = "Mark done";
      btn.addEventListener("click", () => handlers?.onToggleReminder?.(r.id));
      const span = document.createElement("span");
      span.className = "reminder-text";
      span.textContent = r.text;
      li.append(btn, span);
      ul.appendChild(li);
    }
  }
  body.appendChild(ul);

  if (p.canQuickAdd) {
    const row = document.createElement("div");
    row.className = "quick-add-row";
    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Quick add reminder";
    input.setAttribute("aria-label", "Quick add reminder");
    const add = document.createElement("button");
    add.type = "button";
    add.className = "btn";
    add.textContent = "Add";
    const submit = () => {
      const text = input.value.trim();
      if (!text) return;
      handlers?.onAddReminder?.(text);
      input.value = "";
    };
    add.addEventListener("click", submit);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") submit();
    });
    row.append(input, add);
    body.appendChild(row);
  }
}

/**
 * @param {HTMLElement} body
 * @param {{ mode: string; display: object | null }} p
 */
function renderCommute(body, p) {
  const mode = document.createElement("p");
  mode.className = "commute-mode";
  mode.textContent =
    p.mode === "wfh" ? "Work from home" : "Heading to the office";
  body.appendChild(mode);

  if (p.display) {
    const detail = document.createElement("p");
    detail.className = "commute-detail";
    if (p.display.durationMinutes != null) {
      detail.textContent = `~${p.display.durationMinutes} min to ${p.display.label}`;
    } else {
      detail.textContent = p.display.label;
    }
    body.appendChild(detail);
  }
}

/**
 * @param {HTMLElement} body
 * @param {{ links: { label: string; href: string }[] }} p
 */
function renderQuickLinks(body, p) {
  const ul = document.createElement("ul");
  ul.className = "link-list";
  for (const link of p.links) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = link.href;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.textContent = link.label;
    li.appendChild(a);
    ul.appendChild(li);
  }
  body.appendChild(ul);
}

/**
 * @param {HTMLElement} body
 * @param {{ priority: string }} p
 */
function renderFocus(body, p) {
  const input = document.createElement("input");
  input.type = "text";
  input.className = "focus-input";
  input.placeholder = "Today's one priority";
  input.value = p.priority;
  input.setAttribute("aria-label", "Today's focus");
  input.addEventListener("change", () => handlers?.onFocusChange?.(input.value));
  input.addEventListener("blur", () => handlers?.onFocusChange?.(input.value));
  body.appendChild(input);
}

/**
 * @param {string} s
 */
function escapeHtml(s) {
  return s
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
