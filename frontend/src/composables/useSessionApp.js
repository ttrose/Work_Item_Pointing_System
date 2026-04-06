import { computed, onMounted, reactive, ref } from 'vue'
import { io } from 'socket.io-client'

import { API_BASE, SOCKET_URL } from '../config'

const SESSION_STORAGE_ROOM_KEY = 'fusion_poker_joined_room'
const THEME_STORAGE_KEY = 'fusion_poker_theme'

function parseRoomRoute(location) {
  const params = new URLSearchParams(location.search)
  const roomParam = params.get('room') || ''
  const normalizedRoom = roomParam.endsWith('/join') ? roomParam.slice(0, -5) : roomParam
  const joinFromQuery = roomParam.endsWith('/join')
  const joinFromPath = location.pathname.replace(/\/+$/, '').endsWith('/join')

  return {
    roomId: normalizedRoom,
    showJoin: !!normalizedRoom && (joinFromQuery || joinFromPath)
  }
}

export function useSessionApp() {
  const routeState = parseRoomRoute(window.location)
  const createSessionName = ref('Fusion Refinement')
  const roomId = ref(routeState.roomId)
  const requiresJoinConfirmation = ref(routeState.showJoin)
  const joinedRoomId = ref(sessionStorage.getItem(SESSION_STORAGE_ROOM_KEY) || '')

  const activeTab = ref('settings')
  const selectedVote = ref(null)
  const socket = ref(null)
  const dragPointIndex = ref(null)
  const errorMessage = ref('')
  const isDarkMode = ref(localStorage.getItem(THEME_STORAGE_KEY) === 'dark')

  const identity = reactive({
    user_id: localStorage.getItem('fusion_poker_user_id') || crypto.randomUUID(),
    name: localStorage.getItem('fusion_poker_name') || 'Anonymous',
    participant_type: localStorage.getItem('fusion_poker_type') || 'player',
    team: localStorage.getItem('fusion_poker_team') || 'team-1'
  })

  const state = reactive({
    session_name: '',
    story_title: '',
    story_description: '',
    revealed: false,
    settings: {
      show_story_description: true,
      show_history: true,
      show_team_boxes: true,
      allow_show_votes: { players: false, observers: true },
      allow_reset_votes: { players: false, observers: true },
      teams: [{ id: 'team-1', name: 'Team 1' }],
      point_values: []
    },
    work_items: [],
    current_work_item_index: 0,
    current_work_item: null,
    participants: [],
    teams: [],
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
    show_team_boxes: true,
    allow_show_votes: { players: false, observers: true },
    allow_reset_votes: { players: false, observers: true },
    teams: [{ id: 'team-1', name: 'Team 1' }],
    point_values: []
  })

  const draftWorkItems = ref([])

  const isModerator = computed(() => state.moderator_user_id === identity.user_id)
  const canEditIdentityRole = computed(() => isModerator.value && !isLockedModerator.value)
  const isLockedModerator = computed(() => isModerator.value && identity.participant_type === 'observer')
  const showJoinScreen = computed(() => {
    if (!roomId.value) return false
    if (joinedRoomId.value === roomId.value) return false
    return requiresJoinConfirmation.value
  })

  const permissions = computed(() => {
    const isPlayer = identity.participant_type === 'player'
    return {
      can_vote: isPlayer,
      can_show_votes: !!state.settings.allow_show_votes[isPlayer ? 'players' : 'observers'],
      can_reset_votes: !!state.settings.allow_reset_votes[isPlayer ? 'players' : 'observers'],
      can_edit_settings: isModerator.value
    }
  })

  const moderatorName = computed(() => {
    const found = state.participants.find(p => p.user_id === state.moderator_user_id)
    return found ? found.name : ''
  })

  function applyTheme() {
    document.body.classList.toggle('theme-dark', isDarkMode.value)
    localStorage.setItem(THEME_STORAGE_KEY, isDarkMode.value ? 'dark' : 'light')
  }

  function toggleTheme() {
    isDarkMode.value = !isDarkMode.value
    applyTheme()
  }

  function markRoomJoined() {
    joinedRoomId.value = roomId.value
    sessionStorage.setItem(SESSION_STORAGE_ROOM_KEY, roomId.value)
    requiresJoinConfirmation.value = false

    const url = new URL(window.location.href)
    url.searchParams.set('room', roomId.value)
    window.history.replaceState({}, '', url)
  }

  function applyIncomingState(payload) {
    state.session_name = payload.session_name
    state.story_title = payload.story_title
    state.story_description = payload.story_description
    state.revealed = payload.revealed
    state.settings = payload.settings
    state.work_items = payload.work_items
    state.current_work_item_index = payload.current_work_item_index
    state.current_work_item = payload.current_work_item
    state.participants = payload.participants
    state.teams = payload.teams
    state.history = payload.history
    state.moderator_user_id = payload.moderator_user_id

    const me = payload.participants.find(participant => participant.user_id === identity.user_id)
    if (me) {
      identity.name = me.name || identity.name
      identity.participant_type = me.participant_type || identity.participant_type
      identity.team = me.team || ''
      normalizeIdentity()
    }

    if (activeTab.value === 'settings' && !isModerator.value) {
      activeTab.value = 'general'
    }

    localStory.session_name = payload.session_name || ''
    localStory.story_title = payload.story_title || ''
    localStory.story_description = payload.story_description || ''

    draftSettings.show_story_description = payload.settings.show_story_description
    draftSettings.show_history = payload.settings.show_history
    draftSettings.show_team_boxes = payload.settings.show_team_boxes
    draftSettings.allow_show_votes = { ...payload.settings.allow_show_votes }
    draftSettings.allow_reset_votes = { ...payload.settings.allow_reset_votes }
    draftSettings.teams = payload.settings.teams.map(team => ({ ...team }))
    draftSettings.point_values = payload.settings.point_values.map(p => ({ ...p }))
    draftWorkItems.value = payload.work_items.map(item => ({ ...item }))
  }

  async function createRoom() {
    errorMessage.value = ''
    identity.participant_type = 'observer'
    identity.team = ''
    normalizeIdentity()

    try {
      const res = await fetch(`${API_BASE}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_name: createSessionName.value })
      })

      if (!res.ok) {
        throw new Error(`Backend returned ${res.status}`)
      }

      const data = await res.json()
      roomId.value = data.room
      markRoomJoined()
      connectSocket()
    } catch (error) {
      errorMessage.value = `Could not reach the backend at ${API_BASE}. Start the Flask server and try again.`
      console.error(error)
    }
  }

  function normalizeIdentity() {
    if (identity.participant_type === 'observer') {
      identity.team = ''
    } else {
      const availableTeams = state.settings.teams.length ? state.settings.teams : draftSettings.teams
      const validTeamIds = new Set(availableTeams.map(team => team.id))
      if (!identity.team || !validTeamIds.has(identity.team)) {
        identity.team = availableTeams[0]?.id || 'team-1'
      }
    }

    localStorage.setItem('fusion_poker_user_id', identity.user_id)
    localStorage.setItem('fusion_poker_name', identity.name)
    localStorage.setItem('fusion_poker_type', identity.participant_type)
    localStorage.setItem('fusion_poker_team', identity.team)
  }

  function connectSocket() {
    if (!roomId.value || showJoinScreen.value) return
    normalizeIdentity()
    errorMessage.value = ''

    if (socket.value) {
      socket.value.disconnect()
    }

    socket.value = io(SOCKET_URL)

    socket.value.on('connect_error', () => {
      errorMessage.value = `Realtime connection failed. Make sure the backend is running at ${SOCKET_URL}.`
    })

    socket.value.on('connect', () => {
      errorMessage.value = ''
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
      const me = state.teams.flatMap(team => team.participants).find(p => p.user_id === identity.user_id)
      if (!me || !me.has_voted) {
        selectedVote.value = null
      }
    })
  }

  function joinRoom() {
    normalizeIdentity()
    markRoomJoined()
    connectSocket()
  }

  function syncIdentity() {
    if (!isModerator.value) return

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
    if (!isModerator.value) return

    socket.value?.emit('update_story', {
      room: roomId.value,
      user_id: identity.user_id,
      session_name: localStory.session_name,
      story_title: localStory.story_title,
      story_description: localStory.story_description
    })
  }

  function saveSettings() {
    if (!permissions.value.can_edit_settings) return

    socket.value?.emit('update_settings', {
      room: roomId.value,
      user_id: identity.user_id,
      participant_type: identity.participant_type,
      settings: {
        show_story_description: draftSettings.show_story_description,
        show_history: draftSettings.show_history,
        show_team_boxes: draftSettings.show_team_boxes,
        allow_show_votes: draftSettings.allow_show_votes,
        allow_reset_votes: draftSettings.allow_reset_votes,
        teams: draftSettings.teams,
        point_values: draftSettings.point_values
      }
    })
  }

  function saveWorkItems() {
    if (!permissions.value.can_edit_settings) return

    socket.value?.emit('update_work_items', {
      room: roomId.value,
      user_id: identity.user_id,
      current_work_item_id: state.current_work_item?.id,
      work_items: draftWorkItems.value
    })
  }

  function resetDefaults() {
    draftSettings.show_story_description = true
    draftSettings.show_history = true
    draftSettings.show_team_boxes = true
    draftSettings.allow_show_votes = { players: false, observers: true }
    draftSettings.allow_reset_votes = { players: false, observers: true }
    draftSettings.teams = [{ id: 'team-1', name: 'Team 1' }]
    draftSettings.point_values = [
      { label: '0 points', value: '0' },
      { label: '1/2 point', value: '0.5' },
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

  function addWorkItem() {
    draftWorkItems.value.push({
      id: `work-item-${crypto.randomUUID()}`,
      title: `Work Item ${draftWorkItems.value.length + 1}`,
      description: ''
    })
  }

  function removeWorkItem(idx) {
    if (draftWorkItems.value.length === 1) return
    draftWorkItems.value.splice(idx, 1)
  }

  function moveWorkItem(idx, direction) {
    const next = idx + direction
    if (next < 0 || next >= draftWorkItems.value.length) return
    const items = draftWorkItems.value
    ;[items[idx], items[next]] = [items[next], items[idx]]
  }

  function addTeam() {
    draftSettings.teams.push({
      id: `team-${crypto.randomUUID()}`,
      name: `Team ${draftSettings.teams.length + 1}`
    })
  }

  function removeTeam(idx) {
    if (draftSettings.teams.length === 1) return
    draftSettings.teams.splice(idx, 1)
  }

  function addPoint() {
    draftSettings.point_values.push({ label: '', value: '' })
  }

  function removePoint(idx) {
    draftSettings.point_values.splice(idx, 1)
    if (draftSettings.point_values.length === 0) addPoint()
  }

  function startPointDrag(idx) {
    if (!permissions.value.can_edit_settings) return
    dragPointIndex.value = idx
  }

  function dropPoint(idx) {
    if (dragPointIndex.value === null || dragPointIndex.value === idx) return
    const arr = draftSettings.point_values
    const [moved] = arr.splice(dragPointIndex.value, 1)
    arr.splice(idx, 0, moved)
    dragPointIndex.value = null
  }

  function endPointDrag() {
    dragPointIndex.value = null
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
      user_id: identity.user_id,
      participant_type: identity.participant_type
    })
  }

  function resetVotes() {
    selectedVote.value = null
    socket.value?.emit('reset_votes', {
      room: roomId.value,
      user_id: identity.user_id,
      participant_type: identity.participant_type
    })
  }

  function navigateWorkItem(direction) {
    socket.value?.emit('navigate_work_item', {
      room: roomId.value,
      user_id: identity.user_id,
      direction
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

  function teamName(teamId) {
    return state.settings.teams.find(team => team.id === teamId)?.name || teamId
  }

  function formatStat(value) {
    return value === null || value === undefined ? '—' : value
  }

  function consensusBadgeClass(consensus) {
    return consensus ? 'green' : 'orange'
  }

  async function copyRoom() {
    const url = new URL(window.location.href)
    url.searchParams.set('room', `${roomId.value}/join`)
    await navigator.clipboard.writeText(url.toString())
    alert('Join link copied.')
  }

  onMounted(() => {
    applyTheme()
    normalizeIdentity()

    if (roomId.value && !showJoinScreen.value) {
      connectSocket()
    }
  })

  return {
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
    isLockedModerator,
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
  }
}
