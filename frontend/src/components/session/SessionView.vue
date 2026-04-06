<template>
  <div>
    <SessionTopbar
      :canEditIdentityRole="canEditIdentityRole"
      :copyRoom="copyRoom"
      :errorMessage="errorMessage"
      :identity="identity"
      :isModerator="isModerator"
      :localStory="localStory"
      :roomId="roomId"
      :saveStory="saveStory"
      :state="state"
      :syncIdentity="syncIdentity"
    />

    <div class="layout">
      <SessionSidebar
        :activeTab="activeTab"
        :addPoint="addPoint"
        :addTeam="addTeam"
        :addWorkItem="addWorkItem"
        :dragPointIndex="dragPointIndex"
        :draftSettings="draftSettings"
        :draftWorkItems="draftWorkItems"
        :dropPoint="dropPoint"
        :endPointDrag="endPointDrag"
        :isModerator="isModerator"
        :moveWorkItem="moveWorkItem"
        :permissions="permissions"
        :removePoint="removePoint"
        :removeTeam="removeTeam"
        :removeWorkItem="removeWorkItem"
        :resetDefaults="resetDefaults"
        :saveSettings="saveSettings"
        :saveWorkItems="saveWorkItems"
        :startPointDrag="startPointDrag"
        @update:activeTab="$emit('update:activeTab', $event)"
      />

      <SessionMain
        :castVote="castVote"
        :consensusBadgeClass="consensusBadgeClass"
        :formatStat="formatStat"
        :isModerator="isModerator"
        :localStory="localStory"
        :moderatorName="moderatorName"
        :navigateWorkItem="navigateWorkItem"
        :permissions="permissions"
        :prettyParticipant="prettyParticipant"
        :resetVotes="resetVotes"
        :revealVotes="revealVotes"
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
  castVote: { type: Function, required: true },
  consensusBadgeClass: { type: Function, required: true },
  copyRoom: { type: Function, required: true },
  dragPointIndex: { type: [Number, null], required: false, default: null },
  draftSettings: { type: Object, required: true },
  draftWorkItems: { type: Array, required: true },
  dropPoint: { type: Function, required: true },
  endPointDrag: { type: Function, required: true },
  errorMessage: { type: String, required: true },
  formatStat: { type: Function, required: true },
  identity: { type: Object, required: true },
  isModerator: { type: Boolean, required: true },
  localStory: { type: Object, required: true },
  moderatorName: { type: String, required: true },
  moveWorkItem: { type: Function, required: true },
  navigateWorkItem: { type: Function, required: true },
  permissions: { type: Object, required: true },
  prettyParticipant: { type: Function, required: true },
  removePoint: { type: Function, required: true },
  removeTeam: { type: Function, required: true },
  removeWorkItem: { type: Function, required: true },
  resetDefaults: { type: Function, required: true },
  resetVotes: { type: Function, required: true },
  revealVotes: { type: Function, required: true },
  roomId: { type: String, required: true },
  saveSettings: { type: Function, required: true },
  saveStory: { type: Function, required: true },
  saveWorkItems: { type: Function, required: true },
  selectedVote: { type: [String, null], required: false, default: null },
  setModerator: { type: Function, required: true },
  startPointDrag: { type: Function, required: true },
  state: { type: Object, required: true },
  syncIdentity: { type: Function, required: true },
  teamName: { type: Function, required: true },
})

defineEmits(['update:activeTab'])
</script>
