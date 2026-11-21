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
    const { selectedTrack, closePlayer } = useAudioPlayer()
    return { selectedTrack, closePlayer }
  },
  template: '<WorksView /><ClAudioPlayer :track="selectedTrack" @close="closePlayer" />',
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
