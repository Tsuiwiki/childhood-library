import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

// Visual regression reference: the prototypes define the palette, the Vue app
// must copy it verbatim (IMPLEMENTATION_ROADMAP.md T-08 acceptance criteria).
// vitest rewrites import.meta.url to a non-file scheme, so resolve from cwd.
const roots = [process.cwd(), resolve(process.cwd(), 'web')]
const webRoot = roots.find((root) => existsSync(resolve(root, 'src/styles/tokens.css')))
if (!webRoot) throw new Error('cannot locate web/ from the current working directory')
const repoRoot = resolve(webRoot, '..')

const tokens = readFileSync(resolve(webRoot, 'src/styles/tokens.css'), 'utf8')
const music = readFileSync(resolve(repoRoot, 'design-demos/music.html'), 'utf8')
const works = readFileSync(resolve(repoRoot, 'design-demos/works.html'), 'utf8')

const palette: Record<string, string> = {
  '--paper': '#f4eddc',
  '--paper-light': '#fffaf0',
  '--ink': '#191917',
  '--red': '#e64a38',
  '--yellow': '#f1bd32',
  '--blue': '#2858b8',
  '--green': '#739348',
}

describe('visual tokens', () => {
  it('copies every core colour from both prototypes without redefining it', () => {
    for (const [name, value] of Object.entries(palette)) {
      expect(music).toContain(`${name}: ${value}`)
      expect(works).toContain(`${name}: ${value}`)
      expect(tokens).toContain(`${name}: ${value};`)
      expect(tokens.split(`${name}:`).length - 1).toBe(1)
    }
  })

  it('keeps the brown accent from music.html and the signature tokens', () => {
    expect(music).toContain('--brown: #8b5e3c')
    expect(tokens).toContain('--brown: #8b5e3c;')
    expect(tokens).toContain('--line: 3px solid var(--ink);')
    expect(tokens).toContain('--shadow: 7px 7px 0 var(--ink);')
    expect(tokens).toContain('--serif:')
    expect(tokens).toContain('--sans:')
  })

  it('documents the exact source lines in a comment', () => {
    expect(tokens).toContain('design-demos/music.html L9-L15')
    expect(tokens).toContain('design-demos/works.html L9-L20')
  })
})
