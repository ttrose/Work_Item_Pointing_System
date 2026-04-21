<template>
  <div class="shell">
    <ThemeToggle :isDarkMode="isDarkMode" @toggle="toggleTheme" />

    <div v-if="!roomId" class="panel hero">
      <h1>Work Item Planning Session</h1>
      <p class="muted">
        Single-session planning poker with flexible team estimation, moderator controls,
        live settings, and permission-aware actions.
      </p>
      <div v-if="errorMessage" class="alert error">{{ errorMessage }}</div>

      <div class="field">
        <label>Session name</label>
        <input v-model="createSessionName" placeholder="New Session" />
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
            <option v-for="team in joinTeamOptions" :key="team.id || 'no-team'" :value="team.id">{{ team.name }}</option>
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
      :canClaimModerator="canClaimModerator"
      :castVote="castVote"
      :claimModerator="claimModerator"
      :consensusBadgeClass="consensusBadgeClass"
      :copyRoom="copyRoom"
      :dragPointIndex="dragPointIndex"
      :dragWorkItemIndex="dragWorkItemIndex"
      :draftSettings="draftSettings"
      :draftWorkItems="draftWorkItems"
      :dropPoint="dropPoint"
      :dropWorkItem="dropWorkItem"
      :endPointDrag="endPointDrag"
      :endWorkItemDrag="endWorkItemDrag"
      :errorMessage="errorMessage"
      :formatDuration="formatDuration"
      :formatStat="formatStat"
      :getLiveElapsedMs="getLiveElapsedMs"
      :identity="identity"
      :isModerator="isModerator"
      :localStory="localStory"
      :moderatorName="moderatorName"
      :moderatorClaimRole="moderatorClaimRole"
      :navigateWorkItem="navigateWorkItem"
      :pendingTeamChangeRequest="pendingTeamChangeRequest"
      :permissions="permissions"
      :prettyParticipant="prettyParticipant"
      :availableTeamChangeOptions="availableTeamChangeOptions"
      :requestTeamChange="requestTeamChange"
      :removePoint="removePoint"
      :removeTeam="removeTeam"
      :removeWorkItem="removeWorkItem"
      :resetDefaults="resetDefaults"
      :resetVotes="resetVotes"
      :revealVotes="revealVotes"
      :respondTeamChangeRequest="respondTeamChangeRequest"
      :roomId="roomId"
      :saveSettings="saveSettings"
      :saveStory="saveStory"
      :setTeamChangeDraft="setTeamChangeDraft"
      :selectedVote="selectedVote"
      :setModerator="setModerator"
      :setCurrentWorkItem="setCurrentWorkItem"
      :startPointDrag="startPointDrag"
      :startWorkItemDrag="startWorkItemDrag"
      :state="state"
      :syncIdentity="syncIdentity"
      :teamChangeDraft="teamChangeDraft"
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
  canClaimModerator,
  castVote,
  claimModerator,
  consensusBadgeClass,
  copyRoom,
  createRoom,
  createSessionName,
  dragPointIndex,
  dragWorkItemIndex,
  draftSettings,
  draftWorkItems,
  dropPoint,
  dropWorkItem,
  endPointDrag,
  endWorkItemDrag,
  errorMessage,
  formatDuration,
  formatStat,
  getLiveElapsedMs,
  identity,
  isDarkMode,
  isModerator,
  joinRoom,
  joinTeamOptions,
  localStory,
  moderatorName,
  moderatorClaimRole,
  navigateWorkItem,
  normalizeIdentity,
  pendingTeamChangeRequest,
  permissions,
  prettyParticipant,
  requestTeamChange,
  removePoint,
  removeTeam,
  removeWorkItem,
  resetDefaults,
  resetVotes,
  revealVotes,
  respondTeamChangeRequest,
  roomId,
  saveSettings,
  saveStory,
  setTeamChangeDraft,
  selectedVote,
  setModerator,
  setCurrentWorkItem,
  showJoinScreen,
  startPointDrag,
  startWorkItemDrag,
  state,
  syncIdentity,
  teamChangeDraft,
  teamName,
  toggleTheme,
  availableTeamChangeOptions,
} = useSessionApp()
</script>
