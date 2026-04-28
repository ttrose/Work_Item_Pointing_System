<template>
  <div>
    <SessionTopbar
      :canEditIdentityRole="canEditIdentityRole"
      :canClaimModerator="canClaimModerator"
      :copyRoom="copyRoom"
      :errorMessage="errorMessage"
      :identity="identity"
      :isModerator="isModerator"
      :localStory="localStory"
      :pendingTeamChangeRequest="pendingTeamChangeRequest"
      :permissions="permissions"
      :availableTeamChangeOptions="availableTeamChangeOptions"
      :requestTeamChange="requestTeamChange"
      :roomId="roomId"
      :saveStory="saveStory"
      :setTeamChangeDraft="setTeamChangeDraft"
      :state="state"
      :syncIdentity="syncIdentity"
      :teamChangeDraft="teamChangeDraft"
    />

    <div class="layout">
      <SessionSidebar
        :activeTab="activeTab"
        :addPoint="addPoint"
        :addTeam="addTeam"
        :addWorkItem="addWorkItem"
        :dragPointIndex="dragPointIndex"
        :dragWorkItemIndex="dragWorkItemIndex"
        :draftSettings="draftSettings"
        :draftWorkItems="draftWorkItems"
        :dropPoint="dropPoint"
        :dropWorkItem="dropWorkItem"
        :endPointDrag="endPointDrag"
        :endWorkItemDrag="endWorkItemDrag"
        :isModerator="isModerator"
        :permissions="permissions"
        :removePoint="removePoint"
        :removeTeam="removeTeam"
        :removeWorkItem="removeWorkItem"
        :resetDefaults="resetDefaults"
        :saveSettings="saveSettings"
        :selectWorkItem="setCurrentWorkItem"
        :startPointDrag="startPointDrag"
        :startWorkItemDrag="startWorkItemDrag"
        :state="state"
        :getLiveElapsedMs="getLiveElapsedMs"
        @update:activeTab="$emit('update:activeTab', $event)"
      />

      <SessionMain
        :castVote="castVote"
        :consensusBadgeClass="consensusBadgeClass"
        :claimModerator="claimModerator"
        :formatDuration="formatDuration"
        :formatStat="formatStat"
        :getLiveElapsedMs="getLiveElapsedMs"
        :isModerator="isModerator"
        :localStory="localStory"
        :moderatorName="moderatorName"
        :moderatorClaimRole="moderatorClaimRole"
        :navigateWorkItem="navigateWorkItem"
        :permissions="permissions"
        :prettyParticipant="prettyParticipant"
        :resetVotes="resetVotes"
        :revealVotes="revealVotes"
        :respondTeamChangeRequest="respondTeamChangeRequest"
        :saveStory="saveStory"
        :selectedVote="selectedVote"
        :setModerator="setModerator"
        :state="state"
        :teamName="teamName"
      />
    </div>
  </div>
</template>

<script setup>
import SessionMain from './SessionMain.vue'
import SessionSidebar from './SessionSidebar.vue'
import SessionTopbar from './SessionTopbar.vue'

defineProps({
  activeTab: { type: String, required: true },
  addPoint: { type: Function, required: true },
  addTeam: { type: Function, required: true },
  addWorkItem: { type: Function, required: true },
  canEditIdentityRole: { type: Boolean, required: true },
  canClaimModerator: { type: Boolean, required: true },
  castVote: { type: Function, required: true },
  claimModerator: { type: Function, required: true },
  consensusBadgeClass: { type: Function, required: true },
  copyRoom: { type: Function, required: true },
  dragPointIndex: { type: [Number, null], required: false, default: null },
  dragWorkItemIndex: { type: [Number, null], required: false, default: null },
  draftSettings: { type: Object, required: true },
  draftWorkItems: { type: Array, required: true },
  dropPoint: { type: Function, required: true },
  dropWorkItem: { type: Function, required: true },
  endPointDrag: { type: Function, required: true },
  endWorkItemDrag: { type: Function, required: true },
  errorMessage: { type: String, required: true },
  formatDuration: { type: Function, required: true },
  formatStat: { type: Function, required: true },
  getLiveElapsedMs: { type: Function, required: true },
  identity: { type: Object, required: true },
  isModerator: { type: Boolean, required: true },
  localStory: { type: Object, required: true },
  moderatorName: { type: String, required: true },
  moderatorClaimRole: { type: [String, null], required: false, default: null },
  navigateWorkItem: { type: Function, required: true },
  pendingTeamChangeRequest: { type: Object, required: false, default: null },
  permissions: { type: Object, required: true },
  prettyParticipant: { type: Function, required: true },
  availableTeamChangeOptions: { type: Array, required: true },
  requestTeamChange: { type: Function, required: true },
  removePoint: { type: Function, required: true },
  removeTeam: { type: Function, required: true },
  removeWorkItem: { type: Function, required: true },
  resetDefaults: { type: Function, required: true },
  resetVotes: { type: Function, required: true },
  revealVotes: { type: Function, required: true },
  respondTeamChangeRequest: { type: Function, required: true },
  roomId: { type: String, required: true },
  saveSettings: { type: Function, required: true },
  saveStory: { type: Function, required: true },
  setTeamChangeDraft: { type: Function, required: true },
  selectedVote: { type: [String, null], required: false, default: null },
  setModerator: { type: Function, required: true },
  setCurrentWorkItem: { type: Function, required: true },
  startPointDrag: { type: Function, required: true },
  startWorkItemDrag: { type: Function, required: true },
  state: { type: Object, required: true },
  syncIdentity: { type: Function, required: true },
  teamChangeDraft: { type: String, required: true },
  teamName: { type: Function, required: true },
})

defineEmits(['update:activeTab'])
</script>
