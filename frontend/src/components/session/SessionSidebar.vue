<template>
  <aside class="panel sidebar">
    <div class="queue-shell">
      <div class="title-row">
        <div>
          <h3>Work Item Queue</h3>
          <div class="muted">Everyone can follow the queue. Only the moderator can change it.</div>
        </div>
        <button v-if="permissions.can_edit_settings" class="btn ghost" @click="addWorkItem">Add Work Item</button>
      </div>

      <div class="queue-list">
        <div
          v-for="(item, idx) in draftWorkItems"
          :key="item.id"
          class="queue-row"
          :class="{
            active: idx === state.current_work_item_index,
            editable: permissions.can_edit_settings,
            dragging: dragWorkItemIndex === idx
          }"
          @click="permissions.can_edit_settings && selectWorkItem(idx)"
          :draggable="permissions.can_edit_settings"
          @dragstart="startWorkItemDrag(idx)"
          @dragover.prevent
          @drop="dropWorkItem(idx)"
          @dragend="endWorkItemDrag"
        >
          <span
            v-if="permissions.can_edit_settings"
            class="queue-grip"
            aria-hidden="true"
          >
            <span></span>
            <span></span>
            <span></span>
          </span>
          <div class="queue-row-copy">
            <strong>{{ idx + 1 }}. {{ item.title }}</strong>
            <div v-if="item.description" class="small muted">{{ item.description }}</div>
            <div class="small queue-time" :class="{ live: item.timer_started_at }">
              Time spent: {{ formatDuration(getLiveElapsedMs(item)) }}
            </div>
          </div>
          <button
            v-if="permissions.can_edit_settings"
            class="mini"
            type="button"
            :disabled="draftWorkItems.length === 1"
            @click.stop="removeWorkItem(idx)"
          >
            ×
          </button>
        </div>
      </div>
    </div>

    <div class="tabs">
      <button v-if="permissions.can_edit_settings" class="tab" :class="{ active: activeTab === 'settings' }" @click="$emit('update:activeTab', 'settings')">
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

    <div v-if="activeTab === 'settings' && permissions.can_edit_settings">
      <h3>Settings</h3>
      <p class="muted">Settings changes apply live and clear the current round so the point deck and permissions stay in sync.</p>

      <label class="check">
        <input
          type="checkbox"
          v-model="draftSettings.allow_observer_moderator_permissions"
          :disabled="!isModerator"
        />
        All observers can have moderator permissions
      </label>
      <div class="muted small">
        When enabled, observers can edit work items, session content, and approve team changes. Only the current moderator can hand off moderator status or change this toggle.
      </div>

      <div class="team-settings">
        <div class="title-row">
          <h3>Teams</h3>
          <button class="btn ghost" :disabled="!permissions.can_edit_settings" @click="addTeam">+ Team</button>
        </div>
        <div class="muted small">Adding or removing a team saves immediately. Use Save Teams after renaming.</div>

        <div class="team-row" v-for="(team, idx) in draftSettings.teams" :key="team.id">
          <input v-model="team.name" :disabled="!permissions.can_edit_settings" placeholder="Team name" />
          <button class="mini" :disabled="!permissions.can_edit_settings || draftSettings.teams.length === 1" @click="removeTeam(idx)">×</button>
        </div>

        <div class="button-row">
          <button class="btn primary" :disabled="!permissions.can_edit_settings" @click="saveSettings">Save Teams</button>
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
  dragWorkItemIndex: { type: [Number, null], required: false, default: null },
  draftSettings: { type: Object, required: true },
  draftWorkItems: { type: Array, required: true },
  dropPoint: { type: Function, required: true },
  dropWorkItem: { type: Function, required: true },
  endPointDrag: { type: Function, required: true },
  endWorkItemDrag: { type: Function, required: true },
  formatDuration: { type: Function, required: true },
  getLiveElapsedMs: { type: Function, required: true },
  isModerator: { type: Boolean, required: true },
  permissions: { type: Object, required: true },
  removePoint: { type: Function, required: true },
  removeTeam: { type: Function, required: true },
  removeWorkItem: { type: Function, required: true },
  resetDefaults: { type: Function, required: true },
  saveSettings: { type: Function, required: true },
  selectWorkItem: { type: Function, required: true },
  startPointDrag: { type: Function, required: true },
  startWorkItemDrag: { type: Function, required: true },
  state: { type: Object, required: true },
})

defineEmits(['update:activeTab'])
</script>
