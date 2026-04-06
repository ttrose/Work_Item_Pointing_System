<template>
  <div class="panel topbar">
    <div v-if="errorMessage" class="alert error topbar-alert">{{ errorMessage }}</div>
    <div class="field">
      <label>Session</label>
      <input v-model="localStory.session_name" :disabled="!isModerator" @change="saveStory" />
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
  roomId: { type: String, required: true },
  saveStory: { type: Function, required: true },
  state: { type: Object, required: true },
  syncIdentity: { type: Function, required: true },
})
</script>
