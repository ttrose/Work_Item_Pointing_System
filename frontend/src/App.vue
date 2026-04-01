<template>
  <div class="shell">
    <div v-if="!roomId" class="panel hero">
      <h1>Fusion Planning Poker</h1>
      <p class="muted">
        Single-session planning poker with DEV and QA split estimation, moderator controls,
        live settings, and permission-aware actions.
      </p>

      <div class="field">
        <label>Session name</label>
        <input v-model="createSessionName" placeholder="Fusion Refinement" />
      </div>

      <div class="button-row">
        <button class="btn primary" @click="createRoom">Create Session</button>
      </div>
    </div>

    <div v-else>
      <div class="panel topbar">
        <div class="field">
          <label>Session</label>
          <input v-model="localStory.session_name" @change="saveStory" />
          <div class="roomcode">Room code: <strong>{{ roomId }}</strong></div>
        </div>

        <div class="identity">
          <div class="field">
            <label>Name</label>
            <input v-model="identity.name" @change="syncIdentity" />
          </div>

          <div class="field">
            <label>Participation</label>
            <select v-model="identity.participant_type" @change="syncIdentity">
              <option value="player">Player</option>
              <option value="observer">Observer</option>
            </select>
          </div>

          <div class="field">
            <label>Team</label>
            <select
              v-model="identity.team"
              @change="syncIdentity"
              :disabled="identity.participant_type === 'observer'"
            >
              <option value="">No team</option>
              <option value="DEV">DEV</option>
              <option value="QA">QA</option>
            </select>
          </div>
        </div>

        <div class="button-row">
          <button class="btn ghost" @click="copyRoom">Copy Room Link</button>
        </div>
      </div>

      <div class="layout">
        <aside class="panel sidebar">
          <div class="tabs">
            <button class="tab" :class="{ active: activeTab === 'settings' }" @click="activeTab = 'settings'">Settings</button>
            <button class="tab" :class="{ active: activeTab === 'general' }" @click="activeTab = 'general'">General Options</button>
            <button class="tab" :class="{ active: activeTab === 'points' }" @click="activeTab = 'points'">Point Values</button>
          </div>

          <div v-if="!permissions.can_edit_settings" class="badge orange">Observer role required to edit settings</div>

          <div v-if="activeTab === 'settings'">
            <h3>Settings</h3>
            <p class="muted">Changes apply live and clear the current round so the point deck and permissions stay in sync.</p>
            <button class="btn ghost" :disabled="!permissions.can_edit_settings" @click="resetDefaults">
              Reset Settings to Default
            </button>
          </div>

          <div v-if="activeTab === 'general'">
            <h3>General Options</h3>

            <label class="check"><input type="checkbox" v-model="draftSettings.show_story_description" :disabled="!permissions.can_edit_settings" /> Show Story Description</label>
            <label class="check"><input type="checkbox" v-model="draftSettings.show_history" :disabled="!permissions.can_edit_settings" /> Show History</label>

            <h3>Participants allowed to show votes</h3>
            <label class="check"><input type="checkbox" v-model="draftSettings.allow_show_votes.players" :disabled="!permissions.can_edit_settings" /> Players</label>
            <label class="check"><input type="checkbox" v-model="draftSettings.allow_show_votes.observers" :disabled="!permissions.can_edit_settings" /> Observers</label>

            <h3>Participants allowed to reset votes</h3>
            <label class="check"><input type="checkbox" v-model="draftSettings.allow_reset_votes.players" :disabled="!permissions.can_edit_settings" /> Players</label>
            <label class="check"><input type="checkbox" v-model="draftSettings.allow_reset_votes.observers" :disabled="!permissions.can_edit_settings" /> Observers</label>

            <div class="button-row">
              <button class="btn primary" :disabled="!permissions.can_edit_settings" @click="saveSettings">Apply Settings</button>
            </div>
          </div>

          <div v-if="activeTab === 'points'">
            <h3>Point Values</h3>

            <div class="pv-row" v-for="(item, idx) in draftSettings.point_values" :key="idx">
              <input v-model="item.label" :disabled="!permissions.can_edit_settings" placeholder="Label" />
              <input v-model="item.value" :disabled="!permissions.can_edit_settings" placeholder="Value" />
              <div class="mini-actions">
                <button class="mini" :disabled="!permissions.can_edit_settings || idx === 0" @click="movePoint(idx, -1)">↑</button>
                <button class="mini" :disabled="!permissions.can_edit_settings || idx === draftSettings.point_values.length - 1" @click="movePoint(idx, 1)">↓</button>
                <button class="mini" :disabled="!permissions.can_edit_settings" @click="removePoint(idx)">×</button>
              </div>
            </div>

            <div class="button-row">
              <button class="btn ghost" :disabled="!permissions.can_edit_settings" @click="addPoint">Add Value</button>
              <button class="btn primary" :disabled="!permissions.can_edit_settings" @click="saveSettings">Apply Point Values</button>
            </div>
          </div>
        </aside>

        <main class="room">
          <section class="panel section">
            <div class="title-row">
              <div>
                <h2>{{ state.story_title || 'Current Story' }}</h2>
                <div class="muted">{{ state.session_name }}</div>
              </div>
              <div class="button-row">
                <span class="badge blue" v-if="isModerator">Moderator</span>
                <span class="badge green" v-if="state.revealed">Votes Revealed</span>
                <span class="badge" v-else>Votes Hidden</span>
              </div>
            </div>

            <div class="field">
              <label>Story title</label>
              <input v-model="localStory.story_title" @change="saveStory" />
            </div>

            <div v-if="state.settings.show_story_description" class="field">
              <label>Story description</label>
              <textarea v-model="localStory.story_description" @change="saveStory"></textarea>
            </div>

            <div class="button-row">
              <button v-if="permissions.can_show_votes && !state.revealed" class="btn warn" @click="revealVotes">Show Votes</button>
              <button v-if="permissions.can_reset_votes" class="btn danger" @click="resetVotes">Reset Votes</button>
            </div>
          </section>

          <section v-if="permissions.can_vote" class="panel section">
            <div class="title-row">
              <div>
                <h3>Vote deck</h3>
                <div class="muted">One session, split results.</div>
              </div>
              <div class="badge blue" v-if="selectedVote !== null">Selected: {{ selectedVote }}</div>
            </div>

            <div class="card-grid">
              <button
                class="vote-card"
                :class="{ active: selectedVote === item.value }"
                v-for="item in state.settings.point_values"
                :key="item.label + item.value"
                @click="castVote(item.value)"
              >
                <div>{{ item.label }}</div>
                <div class="muted small">{{ item.value }}</div>
              </button>
            </div>
          </section>

          <section class="split">
            <div class="panel team-panel team-dev">
              <div class="team-head">
                <div>
                  <h3>DEV</h3>
                  <div class="muted">Development estimates</div>
                </div>
                <span class="badge" :class="consensusBadgeClass(state.dev.summary.consensus)">
                  {{ state.dev.summary.consensus_label }}
                </span>
              </div>

              <div class="summary-grid">
                <div class="stat"><div class="label">Voted</div><div class="value">{{ state.dev.summary.count_voted }} / {{ state.dev.summary.count_total }}</div></div>
                <div class="stat"><div class="label">Average</div><div class="value">{{ formatStat(state.dev.summary.average) }}</div></div>
                <div class="stat"><div class="label">Min</div><div class="value">{{ formatStat(state.dev.summary.min) }}</div></div>
                <div class="stat"><div class="label">Max</div><div class="value">{{ formatStat(state.dev.summary.max) }}</div></div>
              </div>

              <div class="member-list">
                <div class="member" v-for="person in state.dev.participants" :key="person.user_id">
                  <div>
                    <div class="member-name">{{ person.name }}</div>
                    <div class="role-line">{{ prettyParticipant(person.participant_type) }}</div>
                  </div>
                  <div class="pill" :class="person.vote !== null ? 'vote' : 'hidden'">
                    {{ person.vote !== null ? person.vote : (person.has_voted ? 'Voted' : '—') }}
                  </div>
                </div>
              </div>
            </div>

            <div class="panel team-panel team-qa">
              <div class="team-head">
                <div>
                  <h3>QA</h3>
                  <div class="muted">Quality estimates</div>
                </div>
                <span class="badge" :class="consensusBadgeClass(state.qa.summary.consensus)">
                  {{ state.qa.summary.consensus_label }}
                </span>
              </div>

              <div class="summary-grid">
                <div class="stat"><div class="label">Voted</div><div class="value">{{ state.qa.summary.count_voted }} / {{ state.qa.summary.count_total }}</div></div>
                <div class="stat"><div class="label">Average</div><div class="value">{{ formatStat(state.qa.summary.average) }}</div></div>
                <div class="stat"><div class="label">Min</div><div class="value">{{ formatStat(state.qa.summary.min) }}</div></div>
                <div class="stat"><div class="label">Max</div><div class="value">{{ formatStat(state.qa.summary.max) }}</div></div>
              </div>

              <div class="member-list">
                <div class="member" v-for="person in state.qa.participants" :key="person.user_id">
                  <div>
                    <div class="member-name">{{ person.name }}</div>
                    <div class="role-line">{{ prettyParticipant(person.participant_type) }}</div>
                  </div>
                  <div class="pill" :class="person.vote !== null ? 'vote' : 'hidden'">
                    {{ person.vote !== null ? person.vote : (person.has_voted ? 'Voted' : '—') }}
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section class="panel section">
            <div class="title-row">
              <div>
                <h3>Moderator Controls</h3>
                <div class="muted">Only the current moderator can hand off moderator status.</div>
              </div>
              <div class="badge blue" v-if="moderatorName">Current moderator: {{ moderatorName }}</div>
            </div>

            <div v-for="person in state.participants" :key="person.user_id" class="participant-line">
              <div>
                <strong>{{ person.name }}</strong>
                <span class="small muted">
                  · <template v-if="person.team">{{ person.team }} · </template>{{ prettyParticipant(person.participant_type) }}
                </span>
                <span v-if="person.user_id === state.moderator_user_id" class="moderator"> · moderator</span>
              </div>
              <div>
                <button
                  v-if="isModerator && person.user_id !== state.moderator_user_id && person.participant_type === 'observer'"
                  class="btn ghost"
                  @click="setModerator(person.user_id)"
                >
                  Make Moderator
                </button>
              </div>
            </div>
          </section>

          <section v-if="state.settings.show_history" class="panel section">
            <h3>History</h3>
            <div v-if="state.history.length === 0" class="muted">No prior rounds yet.</div>
            <div v-else class="history-list">
              <div v-for="(item, idx) in state.history" :key="idx" class="history-item">
                <strong>{{ item.story_title }}</strong>
                <div class="small muted">DEV: {{ item.dev_label }}</div>
                <div class="small muted">QA: {{ item.qa_label }}</div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { io } from 'socket.io-client'
import { API_BASE, SOCKET_URL } from './config'

const createSessionName = ref('Fusion Refinement')
const roomId = ref(new URLSearchParams(window.location.search).get('room') || '')

const activeTab = ref('settings')
const selectedVote = ref(null)
const socket = ref(null)

const identity = reactive({
  user_id: localStorage.getItem('fusion_poker_user_id') || crypto.randomUUID(),
  name: localStorage.getItem('fusion_poker_name') || 'Anonymous',
  participant_type: localStorage.getItem('fusion_poker_type') || 'player',
  team: localStorage.getItem('fusion_poker_team') || 'DEV'
})

const state = reactive({
  session_name: '',
  story_title: '',
  story_description: '',
  revealed: false,
  settings: {
    show_story_description: true,
    show_history: true,
    allow_show_votes: { players: false, observers: true },
    allow_reset_votes: { players: false, observers: true },
    point_values: []
  },
  participants: [],
  dev: { participants: [], summary: {} },
  qa: { participants: [], summary: {} },
  history: [],
  moderator_user_id: null
})

const localStory = reactive({
  session_name: '',
  story_title: '',
  story_description: ''
})

const draftSettings = reactive({
  show_story_description: true,
  show_history: true,
  allow_show_votes: { players: false, observers: true },
  allow_reset_votes: { players: false, observers: true },
  point_values: []
})

const permissions = computed(() => {
  const isPlayer = identity.participant_type === 'player'
  return {
    can_vote: isPlayer,
    can_show_votes: !!state.settings.allow_show_votes[isPlayer ? 'players' : 'observers'],
    can_reset_votes: !!state.settings.allow_reset_votes[isPlayer ? 'players' : 'observers'],
    can_edit_settings: !isPlayer
  }
})

const isModerator = computed(() => state.moderator_user_id === identity.user_id)
const moderatorName = computed(() => {
  const found = state.participants.find(p => p.user_id === state.moderator_user_id)
  return found ? found.name : ''
})

function applyIncomingState(payload) {
  state.session_name = payload.session_name
  state.story_title = payload.story_title
  state.story_description = payload.story_description
  state.revealed = payload.revealed
  state.settings = payload.settings
  state.participants = payload.participants
  state.dev = payload.dev
  state.qa = payload.qa
  state.history = payload.history
  state.moderator_user_id = payload.moderator_user_id

  localStory.session_name = payload.session_name || ''
  localStory.story_title = payload.story_title || ''
  localStory.story_description = payload.story_description || ''

  draftSettings.show_story_description = payload.settings.show_story_description
  draftSettings.show_history = payload.settings.show_history
  draftSettings.allow_show_votes = { ...payload.settings.allow_show_votes }
  draftSettings.allow_reset_votes = { ...payload.settings.allow_reset_votes }
  draftSettings.point_values = payload.settings.point_values.map(p => ({ ...p }))
}

async function createRoom() {
  const res = await fetch(`${API_BASE}/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_name: createSessionName.value })
  })
  const data = await res.json()
  roomId.value = data.room
  const url = new URL(window.location.href)
  url.searchParams.set('room', roomId.value)
  window.history.replaceState({}, '', url)
  connectSocket()
}

function normalizeIdentity() {
  if (identity.participant_type === 'observer') {
    identity.team = ''
  } else if (!identity.team) {
    identity.team = 'DEV'
  }

  localStorage.setItem('fusion_poker_user_id', identity.user_id)
  localStorage.setItem('fusion_poker_name', identity.name)
  localStorage.setItem('fusion_poker_type', identity.participant_type)
  localStorage.setItem('fusion_poker_team', identity.team)
}

function connectSocket() {
  if (!roomId.value) return
  normalizeIdentity()

  if (socket.value) {
    socket.value.disconnect()
  }

  socket.value = io(SOCKET_URL)

  socket.value.on('connect', () => {
    socket.value.emit('join', {
      room: roomId.value,
      user_id: identity.user_id,
      name: identity.name,
      participant_type: identity.participant_type,
      team: identity.team
    })
  })

  socket.value.on('state', payload => {
    applyIncomingState(payload)
    const me = [...state.dev.participants, ...state.qa.participants].find(p => p.user_id === identity.user_id)
    if (!me || !me.has_voted) {
      selectedVote.value = null
    }
  })
}

function syncIdentity() {
  normalizeIdentity()
  selectedVote.value = null
  socket.value?.emit('update_presence', {
    room: roomId.value,
    user_id: identity.user_id,
    name: identity.name,
    participant_type: identity.participant_type,
    team: identity.team
  })
}

function saveStory() {
  socket.value?.emit('update_story', {
    room: roomId.value,
    session_name: localStory.session_name,
    story_title: localStory.story_title,
    story_description: localStory.story_description
  })
}

function saveSettings() {
  socket.value?.emit('update_settings', {
    room: roomId.value,
    participant_type: identity.participant_type,
    settings: {
      show_story_description: draftSettings.show_story_description,
      show_history: draftSettings.show_history,
      allow_show_votes: draftSettings.allow_show_votes,
      allow_reset_votes: draftSettings.allow_reset_votes,
      point_values: draftSettings.point_values
    }
  })
}

function resetDefaults() {
  draftSettings.show_story_description = true
  draftSettings.show_history = true
  draftSettings.allow_show_votes = { players: false, observers: true }
  draftSettings.allow_reset_votes = { players: false, observers: true }
  draftSettings.point_values = [
    { label: '0 points', value: '0' },
    { label: '½ point', value: '0.5' },
    { label: '1 point', value: '1' },
    { label: '2 points', value: '2' },
    { label: '3 points', value: '3' },
    { label: '5 points', value: '5' },
    { label: '8 points', value: '8' },
    { label: '13 points', value: '13' },
    { label: '20 points', value: '20' },
    { label: '40 points', value: '40' },
    { label: '100 points', value: '100' },
    { label: '?', value: '?' }
  ]
  saveSettings()
}

function addPoint() {
  draftSettings.point_values.push({ label: '', value: '' })
}

function removePoint(idx) {
  draftSettings.point_values.splice(idx, 1)
  if (draftSettings.point_values.length === 0) addPoint()
}

function movePoint(idx, direction) {
  const next = idx + direction
  if (next < 0 || next >= draftSettings.point_values.length) return
  const arr = draftSettings.point_values
  ;[arr[idx], arr[next]] = [arr[next], arr[idx]]
}

function castVote(value) {
  if (!permissions.value.can_vote) return
  selectedVote.value = value
  socket.value?.emit('vote', {
    room: roomId.value,
    user_id: identity.user_id,
    value
  })
}

function revealVotes() {
  socket.value?.emit('reveal', {
    room: roomId.value,
    participant_type: identity.participant_type
  })
}

function resetVotes() {
  selectedVote.value = null
  socket.value?.emit('reset_votes', {
    room: roomId.value,
    participant_type: identity.participant_type
  })
}

function setModerator(targetUserId) {
  socket.value?.emit('set_moderator', {
    room: roomId.value,
    requester_user_id: identity.user_id,
    target_user_id: targetUserId
  })
}

function prettyParticipant(value) {
  return value === 'observer' ? 'Observer' : 'Player'
}

function formatStat(value) {
  return value === null || value === undefined ? '—' : value
}

function consensusBadgeClass(consensus) {
  return consensus ? 'green' : 'orange'
}

async function copyRoom() {
  const url = new URL(window.location.href)
  url.searchParams.set('room', roomId.value)
  await navigator.clipboard.writeText(url.toString())
  alert('Room link copied.')
}

onMounted(() => {
  if (roomId.value) {
    connectSocket()
  }
})
</script>
