import { ref } from 'vue'
import type { AudioPlayerTrack } from '@/components/ClAudioPlayer.vue'

// Module-scoped state survives route-view unmounts; the only audio element lives in App.vue.
const selectedTrack = ref<AudioPlayerTrack | null>(null)

export function useAudioPlayer() {
  function playTrack(track: AudioPlayerTrack): void {
    selectedTrack.value = track
  }

  function closePlayer(): void {
    selectedTrack.value = null
  }

  function stopVersion(workId: string, source: string): void {
    if (selectedTrack.value?.id === workId && selectedTrack.value.source !== source) {
      closePlayer()
    }
  }

  return { selectedTrack, playTrack, closePlayer, stopVersion }
}
