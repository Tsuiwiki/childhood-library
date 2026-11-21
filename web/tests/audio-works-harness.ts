import { enableAutoUnmount, mount } from '@vue/test-utils'
import { afterEach } from 'vitest'
import { defineComponent } from 'vue'
import ClAudioPlayer from '../src/components/ClAudioPlayer.vue'
import { useAudioPlayer } from '../src/composables/useAudioPlayer'
import WorksView from '../src/views/WorksView.vue'

enableAutoUnmount(afterEach)

const AudioWorksHarness = defineComponent({
  components: { WorksView, ClAudioPlayer },
  setup() {
    const {
      selectedTrack,
      playlistPosition,
      playlistLength,
      nextTrack,
      previousTrack,
      closePlayer,
    } = useAudioPlayer()
    return { selectedTrack, playlistPosition, playlistLength, nextTrack, previousTrack, closePlayer }
  },
  template: '<WorksView /><ClAudioPlayer :track="selectedTrack" :playlist-position="playlistPosition" :playlist-length="playlistLength" @next="nextTrack" @previous="previousTrack" @close="closePlayer" />',
})

export function mountAudioWorks(attach = false) {
  return mount(AudioWorksHarness, {
    attachTo: attach ? document.body : undefined,
    global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
  })
}

export function resetSharedPlayer(): void {
  useAudioPlayer().closePlayer()
}
