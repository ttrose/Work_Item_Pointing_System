<template>
  <aside class="panel sidebar">
    <div class="tabs">
      <button v-if="isModerator" class="tab" :class="{ active: activeTab === 'settings' }" @click="$emit('update:activeTab', 'settings')">
        Settings
      </button>
      <button class="tab" :class="{ active: activeTab === 'general' }" @click="$emit('update:activeTab', 'general')">
        General Options
      </button>
      <button class="tab" :class="{ active: activeTab === 'points' }" @click="$emit('update:activeTab', 'points')">
        Point Values
      </button>
    </div>

    <div v-if="!permissions.can_edit_settings" class="badge orange">Moderator access required</div>

    <div v-if="activeTab === 'settings' && isModerator">
      <h3>Settings</h3>
      <p class="muted">Changes apply live and clear the current round so the point deck and permissions stay in sync.</p>

      <div class="queue-settings">
        <div class="title-row">
          <h3>Work Item Queue</h3>
          <button class="btn ghost" :disabled="!permissions.can_edit_settings" @click="addWorkItem">Add Work Item</button>
        </div>

        <div class="queue-item" v-for="(item, idx) in draftWorkItems" :key="item.id">
          <div class="queue-item-head">
            <strong>Item {{ idx + 1 }}</strong>
            <div class="mini-actions">
              <button class="mini" :disabled="!permissions.can_edit_settings || idx === 0" @click="moveWorkItem(idx, -1)">↑</button>
              <button class="mini" :disabled="!permissions.can_edit_settings || idx === draftWorkItems.length - 1" @click="moveWorkItem(idx, 1)">↓</button>
              <button class="mini" :disabled="!permissions.can_edit_settings || draftWorkItems.length === 1" @click="removeWorkItem(idx)">×</button>
            </div>
          </div>
          <input v-model="item.title" :disabled="!permissions.can_edit_settings" placeholder="Work item title" />
          <textarea v-model="item.description" :disabled="!permissions.can_edit_settings" placeholder="Work item description"></textarea>
        </div>

        <div class="button-row">
          <button class="btn primary" :disabled="!permissions.can_edit_settings" @click="saveWorkItems">Apply Work Items</button>
        </div>
      </div>

      <div class="team-settings">
        <div class="title-row">
          <h3>Teams</h3>
          <button class="btn ghost" :disabled="!permissions.can_edit_settings" @click="addTeam">+ Team</button>
        </div>

        <div class="team-row" v-for="(team, idx) in draftSettings.teams" :key="team.id">
          <input v-model="team.name" :disabled="!permissions.can_edit_settings" placeholder="Team name" />
          <button class="mini" :disabled="!permissions.can_edit_settings || draftSettings.teams.length === 1" @click="removeTeam(idx)">×</button>
        </div>
      </div>

      <button class="btn ghost" :disabled="!permissions.can_edit_settings" @click="resetDefaults">
        Reset Settings to Default
      </button>
    </div>

    <div v-if="activeTab === 'general'">
      <h3>General Options</h3>

      <label class="check"><input type="checkbox" v-model="draftSettings.show_story_description" :disabled="!permissions.can_edit_settings" /> Show Work Item Description</label>
      <label class="check"><input type="checkbox" v-model="draftSettings.show_history" :disabled="!permissions.can_edit_settings" /> Show History</label>
      <label class="check"><input type="checkbox" v-model="draftSettings.show_team_boxes" :disabled="!permissions.can_edit_settings" /> Show each team in its own box</label>

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

      <div
        class="pv-row"
        :class="{ dragging: dragPointIndex === idx }"
        v-for="(item, idx) in draftSettings.point_values"
        :key="idx"
        :draggable="permissions.can_edit_settings"
        @dragstart="startPointDrag(idx)"
        @dragover.prevent
        @drop="dropPoint(idx)"
        @dragend="endPointDrag"
      >
        <button class="drag-handle" type="button" :disabled="!permissions.can_edit_settings" aria-label="Reorder point value">
          <span></span>
          <span></span>
          <span></span>
        </button>
        <input v-model="item.label" :disabled="!permissions.can_edit_settings" placeholder="Label" />
        <input v-model="item.value" :disabled="!permissions.can_edit_settings" placeholder="Value" />
        <div class="mini-actions">
          <button class="mini" :disabled="!permissions.can_edit_settings" @click="removePoint(idx)">×</button>
        </div>
      </div>

      <div class="button-row">
        <button class="btn ghost" :disabled="!permissions.can_edit_settings" @click="addPoint">Add Value</button>
        <button class="btn primary" :disabled="!permissions.can_edit_settings" @click="saveSettings">Apply Point Values</button>
      </div>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  activeTab: { type: String, required: true },
  addPoint: { type: Function, required: true },
  addTeam: { type: Function, required: true },
  addWorkItem: { type: Function, required: true },
  dragPointIndex: { type: [Number, null], required: false, default: null },
  draftSettings: { type: Object, required: true },
  draftWorkItems: { type: Array, required: true },
  dropPoint: { type: Function, required: true },
  endPointDrag: { type: Function, required: true },
  isModerator: { type: Boolean, required: true },
  moveWorkItem: { type: Function, required: true },
  permissions: { type: Object, required: true },
  removePoint: { type: Function, required: true },
  removeTeam: { type: Function, required: true },
  removeWorkItem: { type: Function, required: true },
  resetDefaults: { type: Function, required: true },
  saveSettings: { type: Function, required: true },
  saveWorkItems: { type: Function, required: true },
  startPointDrag: { type: Function, required: true },
})

defineEmits(['update:activeTab'])
</script>
