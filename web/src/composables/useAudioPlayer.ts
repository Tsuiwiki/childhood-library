import { computed, ref } from 'vue'
import type { AudioPlayerTrack } from '@/components/ClAudioPlayer.vue'

// Module-scoped state survives route-view unmounts; the only audio element lives in App.vue.
const selectedTrack = ref<AudioPlayerTrack | null>(null)
const playlist = ref<AudioPlayerTrack[]>([])
const playlistIndex = ref(-1)
const playlistPosition = computed(() => playlistIndex.value + 1)
const playlistLength = computed(() => playlist.value.length)

function clearPlaylist(): void {
  playlist.value = []
  playlistIndex.value = -1
}

function selectPlaylistTrack(index: number): void {
  playlistIndex.value = index
  selectedTrack.value = { ...playlist.value[index] }
}

export function useAudioPlayer() {
  function playTrack(track: AudioPlayerTrack): void {
    const index = playlist.value.findIndex((item) =>
      item.id === track.id && item.kind === track.kind && item.source === track.source
    )
    if (index >= 0) {
      selectPlaylistTrack(index)
      return
    }
    clearPlaylist()
    selectedTrack.value = track
  }

  function playPlaylist(tracks: AudioPlayerTrack[]): void {
    if (!tracks.length) {
      closePlayer()
      return
    }
    // Keep the launch-time result snapshot, including results on other pages.
    playlist.value = [...tracks]
    selectPlaylistTrack(0)
  }

  function nextTrack(): void {
    if (!playlist.value.length) return
    selectPlaylistTrack((playlistIndex.value + 1) % playlist.value.length)
  }

  function previousTrack(): void {
    if (!playlist.value.length) return
    selectPlaylistTrack((playlistIndex.value - 1 + playlist.value.length) % playlist.value.length)
  }

  function closePlayer(): void {
    selectedTrack.value = null
    clearPlaylist()
  }

  function stopVersion(workId: string, source: string): void {
    if (selectedTrack.value?.id === workId && selectedTrack.value.source !== source) {
      closePlayer()
    }
  }

  return {
    selectedTrack,
    playlistPosition,
    playlistLength,
    playTrack,
    playPlaylist,
    nextTrack,
    previousTrack,
    closePlayer,
    stopVersion,
  }
}
