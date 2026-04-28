<template>
  <div class="panel topbar">
    <div v-if="errorMessage" class="alert error topbar-alert">{{ errorMessage }}</div>
    <div class="field">
      <label>Session</label>
      <input v-model="localStory.session_name" :disabled="!permissions.can_edit_settings" @change="saveStory" />
      <div class="roomcode">Room code: <strong>{{ roomId }}</strong></div>
    </div>

    <div class="identity">
      <div class="field">
        <label>Name</label>
        <input v-model="identity.name" :disabled="!isModerator" @change="syncIdentity" />
      </div>

      <div class="field">
        <label>Participation</label>
        <select v-model="identity.participant_type" :disabled="!canEditIdentityRole" @change="syncIdentity">
          <option value="player">Player</option>
          <option value="observer">Observer</option>
        </select>
      </div>

      <div class="field">
        <label>Team</label>
        <select
          v-model="identity.team"
          :disabled="!canEditIdentityRole || identity.participant_type === 'observer'"
          @change="syncIdentity"
        >
          <option value="">No team</option>
          <option v-for="team in state.settings.teams" :key="team.id" :value="team.id">{{ team.name }}</option>
        </select>
      </div>
    </div>

    <div v-if="identity.participant_type === 'player' && !isModerator" class="team-request-row">
      <div class="field">
        <label>Request Team Change</label>
        <select
          :value="teamChangeDraft"
          @change="setTeamChangeDraft($event.target.value)"
          :disabled="availableTeamChangeOptions.length === 0 || !!pendingTeamChangeRequest"
        >
          <option value="" disabled>{{ availableTeamChangeOptions.length ? 'Choose a team' : 'No other teams available' }}</option>
          <option v-for="team in availableTeamChangeOptions" :key="team.id" :value="team.id">{{ team.name }}</option>
        </select>
        <div v-if="pendingTeamChangeRequest" class="small muted">
          Pending request: {{ pendingTeamChangeRequest.current_team_name }} to {{ pendingTeamChangeRequest.target_team_name }}
        </div>
      </div>

      <div class="button-row">
        <button
          class="btn ghost"
          :disabled="!teamChangeDraft || !!pendingTeamChangeRequest || availableTeamChangeOptions.length === 0"
          @click="requestTeamChange"
        >
          Request Team Change
        </button>
      </div>
    </div>

    <div class="button-row">
      <button class="btn ghost" @click="copyRoom">Copy Join Link</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  canEditIdentityRole: { type: Boolean, required: true },
  copyRoom: { type: Function, required: true },
  errorMessage: { type: String, required: true },
  identity: { type: Object, required: true },
  isModerator: { type: Boolean, required: true },
  localStory: { type: Object, required: true },
  pendingTeamChangeRequest: { type: Object, required: false, default: null },
  permissions: { type: Object, required: true },
  availableTeamChangeOptions: { type: Array, required: true },
  requestTeamChange: { type: Function, required: true },
  roomId: { type: String, required: true },
  saveStory: { type: Function, required: true },
  setTeamChangeDraft: { type: Function, required: true },
  state: { type: Object, required: true },
  syncIdentity: { type: Function, required: true },
  teamChangeDraft: { type: String, required: true },
})
</script>
