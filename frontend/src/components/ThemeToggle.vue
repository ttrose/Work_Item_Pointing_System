<template>
  <div class="shell-actions">
    <button class="btn ghost theme-toggle" @click="$emit('toggle')">
      {{ isDarkMode ? 'Light Mode' : 'Dark Mode' }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  isDarkMode: {
    type: Boolean,
    required: true,
  },
})

defineEmits(['toggle'])
</script>
