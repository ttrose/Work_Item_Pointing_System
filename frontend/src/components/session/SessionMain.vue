<template>
  <main class="room">
    <section class="panel section">
      <div class="title-row">
        <div>
          <h2>{{ state.story_title || 'Current Work Item' }}</h2>
          <div class="muted">{{ state.session_name }}</div>
        </div>
        <div class="button-row">
          <span class="badge">Item {{ state.current_work_item_index + 1 }} of {{ state.work_items.length }}</span>
          <span class="badge timer-badge" :class="{ live: state.current_work_item?.timer_started_at }">
            Time Spent: {{ formatDuration(getLiveElapsedMs(state.current_work_item)) }}
          </span>
          <span class="badge blue" v-if="isModerator">Moderator</span>
          <span class="badge green" v-if="state.revealed">Votes Revealed</span>
          <span class="badge" v-else>Votes Hidden</span>
        </div>
      </div>

      <div class="field">
        <label>Work item title</label>
        <input v-model="localStory.story_title" :disabled="!permissions.can_edit_settings" @change="saveStory" />
      </div>

      <div v-if="state.settings.show_story_description" class="field">
        <label>Work item description</label>
        <textarea v-model="localStory.story_description" :disabled="!permissions.can_edit_settings" @change="saveStory"></textarea>
      </div>

      <div class="button-row">
        <button v-if="permissions.can_show_votes && !state.revealed" class="btn warn" @click="revealVotes">Show Votes</button>
        <button v-if="permissions.can_reset_votes" class="btn danger" @click="resetVotes">Reset Votes</button>
        <button v-if="permissions.can_edit_settings && state.current_work_item_index > 0" class="btn ghost" @click="navigateWorkItem('previous')">Previous Item</button>
        <button v-if="permissions.can_edit_settings && state.current_work_item_index < state.work_items.length - 1" class="btn primary" @click="navigateWorkItem('next')">Next Item</button>
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

    <section class="split" :class="{ stacked: !state.settings.show_team_boxes }">
      <div class="panel team-panel" v-for="team in state.teams" :key="team.id">
        <div class="team-head">
          <div>
            <h3>{{ team.name }}</h3>
            <div class="muted">Team estimates</div>
          </div>
          <span class="badge" :class="consensusBadgeClass(team.summary.consensus)">
            {{ team.summary.consensus_label }}
          </span>
        </div>

        <div class="summary-grid">
          <div class="stat"><div class="label">Voted</div><div class="value">{{ team.summary.count_voted }} / {{ team.summary.count_total }}</div></div>
          <div class="stat"><div class="label">Average</div><div class="value">{{ formatStat(team.summary.average) }}</div></div>
          <div class="stat"><div class="label">Min</div><div class="value">{{ formatStat(team.summary.min) }}</div></div>
          <div class="stat"><div class="label">Max</div><div class="value">{{ formatStat(team.summary.max) }}</div></div>
        </div>

        <div class="member-list">
          <div class="member" v-for="person in team.participants" :key="person.user_id">
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
        <div class="badge orange" v-else>No moderator assigned</div>
      </div>

      <div v-if="canClaimModerator" class="request-card">
        <div>
          <strong>Moderator role is available</strong>
          <div class="small muted">
            <template v-if="moderatorClaimRole === 'observer'">
              An observer can claim moderator access because the previous moderator left.
            </template>
            <template v-else>
              A player can claim moderator access because no observers are currently in the session.
            </template>
          </div>
        </div>
        <div class="mini-actions">
          <button class="btn primary" @click="claimModerator">Claim Moderator Role</button>
        </div>
      </div>

      <div v-for="person in state.participants" :key="person.user_id" class="participant-line">
        <div>
          <strong>{{ person.name }}</strong>
          <span class="small muted">
            · <template v-if="person.team">{{ teamName(person.team) }} · </template>{{ prettyParticipant(person.participant_type) }}
          </span>
          <span v-if="person.user_id === state.moderator_user_id" class="moderator"> · moderator</span>
        </div>
        <div>
          <button v-if="isModerator && person.user_id !== state.moderator_user_id" class="btn ghost" @click="setModerator(person.user_id)">
            Make Moderator
          </button>
        </div>
      </div>

      <div v-if="permissions.can_edit_settings" class="team-change-requests">
        <h3>Team Change Requests</h3>
        <div v-if="state.team_change_requests.length === 0" class="muted">No pending team change requests.</div>
        <div v-for="request in state.team_change_requests" :key="request.request_id" class="request-card">
          <div>
            <strong>{{ request.user_name }}</strong>
            <div class="small muted">{{ request.current_team_name }} to {{ request.target_team_name }}</div>
          </div>
          <div class="mini-actions">
            <button class="btn primary" @click="respondTeamChangeRequest(request.request_id, 'approve')">Approve</button>
            <button class="btn ghost" @click="respondTeamChangeRequest(request.request_id, 'decline')">Decline</button>
          </div>
        </div>
      </div>
    </section>

    <section v-if="state.settings.show_history" class="panel section">
      <h3>History</h3>
      <div v-if="state.history.length === 0" class="muted">No prior rounds yet.</div>
      <div v-else class="history-list">
        <div v-for="(item, idx) in state.history" :key="idx" class="history-item">
          <strong>#{{ item.work_item_number }} · {{ item.work_item_title }}</strong>
          <div class="small history-time">Time spent: {{ formatDuration(item.elapsed_ms) }}</div>
          <div v-if="item.work_item_description" class="small muted">{{ item.work_item_description }}</div>
          <div v-for="teamResult in item.team_results" :key="teamResult.team_id" class="small muted">
            {{ teamResult.team_name }}: {{ teamResult.label }}
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
defineProps({
  canClaimModerator: { type: Boolean, required: true },
  castVote: { type: Function, required: true },
  claimModerator: { type: Function, required: true },
  consensusBadgeClass: { type: Function, required: true },
  formatDuration: { type: Function, required: true },
  formatStat: { type: Function, required: true },
  getLiveElapsedMs: { type: Function, required: true },
  isModerator: { type: Boolean, required: true },
  localStory: { type: Object, required: true },
  moderatorName: { type: String, required: true },
  moderatorClaimRole: { type: [String, null], required: false, default: null },
  navigateWorkItem: { type: Function, required: true },
  permissions: { type: Object, required: true },
  prettyParticipant: { type: Function, required: true },
  resetVotes: { type: Function, required: true },
  revealVotes: { type: Function, required: true },
  respondTeamChangeRequest: { type: Function, required: true },
  saveStory: { type: Function, required: true },
  selectedVote: { type: [String, null], required: false, default: null },
  setModerator: { type: Function, required: true },
  state: { type: Object, required: true },
  teamName: { type: Function, required: true },
})
</script>
