<template>
  <div class="shell">
    <ThemeToggle :isDarkMode="isDarkMode" @toggle="toggleTheme" />

    <div v-if="!roomId" class="panel hero">
      <h1>Fusion Planning Poker</h1>
      <p class="muted">
        Single-session planning poker with flexible team estimation, moderator controls,
        live settings, and permission-aware actions.
      </p>
      <div v-if="errorMessage" class="alert error">{{ errorMessage }}</div>

      <div class="field">
        <label>Session name</label>
        <input v-model="createSessionName" placeholder="Fusion Refinement" />
      </div>

      <div class="field">
        <label>Your name</label>
        <input v-model="identity.name" placeholder="Moderator name" />
      </div>

      <div class="button-row">
        <button class="btn primary" @click="createRoom">Create Session</button>
      </div>
    </div>

    <div v-else-if="showJoinScreen" class="panel hero">
      <h1>Join Session</h1>
      <p class="muted">
        Confirm who is joining room <strong>{{ roomId }}</strong> before entering the session.
      </p>
      <div v-if="errorMessage" class="alert error">{{ errorMessage }}</div>

      <div class="field">
        <label>Name</label>
        <input v-model="identity.name" placeholder="Your name" />
      </div>

      <div class="identity join-grid">
        <div class="field">
          <label>Participation</label>
          <select v-model="identity.participant_type" @change="normalizeIdentity">
            <option value="player">Player</option>
            <option value="observer">Observer</option>
          </select>
        </div>

        <div class="field">
          <label>Team</label>
          <select
            v-model="identity.team"
            @change="normalizeIdentity"
            :disabled="identity.participant_type === 'observer'"
          >
            <option value="">No team</option>
            <option v-for="team in state.settings.teams" :key="team.id" :value="team.id">{{ team.name }}</option>
          </select>
        </div>
      </div>

      <div class="button-row">
        <button class="btn primary" @click="joinRoom">Join Session</button>
      </div>
    </div>

    <SessionView
      v-else
      :activeTab="activeTab"
      :addPoint="addPoint"
      :addTeam="addTeam"
      :addWorkItem="addWorkItem"
      :canEditIdentityRole="canEditIdentityRole"
      :castVote="castVote"
      :consensusBadgeClass="consensusBadgeClass"
      :copyRoom="copyRoom"
      :dragPointIndex="dragPointIndex"
      :draftSettings="draftSettings"
      :draftWorkItems="draftWorkItems"
      :dropPoint="dropPoint"
      :endPointDrag="endPointDrag"
      :errorMessage="errorMessage"
      :formatStat="formatStat"
      :identity="identity"
      :isModerator="isModerator"
      :localStory="localStory"
      :moderatorName="moderatorName"
      :moveWorkItem="moveWorkItem"
      :navigateWorkItem="navigateWorkItem"
      :permissions="permissions"
      :prettyParticipant="prettyParticipant"
      :removePoint="removePoint"
      :removeTeam="removeTeam"
      :removeWorkItem="removeWorkItem"
      :resetDefaults="resetDefaults"
      :resetVotes="resetVotes"
      :revealVotes="revealVotes"
      :roomId="roomId"
      :saveSettings="saveSettings"
      :saveStory="saveStory"
      :saveWorkItems="saveWorkItems"
      :selectedVote="selectedVote"
      :setModerator="setModerator"
      :startPointDrag="startPointDrag"
      :state="state"
      :syncIdentity="syncIdentity"
      :teamName="teamName"
      @update:activeTab="activeTab = $event"
    />

    <DonateFooter />
  </div>
</template>

<script setup>
import DonateFooter from './components/DonateFooter.vue'
import ThemeToggle from './components/ThemeToggle.vue'
import SessionView from './components/session/SessionView.vue'
import { useSessionApp } from './composables/useSessionApp'

const {
  activeTab,
  addPoint,
  addTeam,
  addWorkItem,
  canEditIdentityRole,
  castVote,
  consensusBadgeClass,
  copyRoom,
  createRoom,
  createSessionName,
  dragPointIndex,
  draftSettings,
  draftWorkItems,
  dropPoint,
  endPointDrag,
  errorMessage,
  formatStat,
  identity,
  isDarkMode,
  isModerator,
  joinRoom,
  localStory,
  moderatorName,
  moveWorkItem,
  navigateWorkItem,
  normalizeIdentity,
  permissions,
  prettyParticipant,
  removePoint,
  removeTeam,
  removeWorkItem,
  resetDefaults,
  resetVotes,
  revealVotes,
  roomId,
  saveSettings,
  saveStory,
  saveWorkItems,
  selectedVote,
  setModerator,
  showJoinScreen,
  startPointDrag,
  state,
  syncIdentity,
  teamName,
  toggleTheme,
} = useSessionApp()
</script>
