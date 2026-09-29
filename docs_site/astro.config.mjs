import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import versionsConfig from './versions.json' with { type: 'json' };

// https://astro.build/config
export default defineConfig({
  site: 'https://nexusnv.github.io',
  base: '/adhan-py',
  vite: {
    resolve: {
      preserveSymlinks: true,
    },
  },
  integrations: [
    starlight({
      title: 'adhan-py',
      description: 'An offline Python library for calculating Islamic prayer times.',
      logo: {
        src: './public/favicon.svg',
      },
      social: [
        { label: 'GitHub', href: 'https://github.com/nexusnv/adhan-py', icon: 'github' },
      ],
      editLink: {
        baseUrl: 'https://github.com/nexusnv/adhan-py/edit/main/docs/user/',
      },
      lastUpdated: true,
      expressiveCode: {
        styleOverrides: {
          borderRadius: '0.375rem',
        },
      },
      sidebar: [
        {
          label: 'Home',
          link: '/',
        },
        {
          label: 'Getting Started',
          link: '/getting-started/',
        },
        {
          label: 'Calculation Methods',
          link: '/calculation-methods/',
        },
        {
          label: 'Polar Regions',
          link: '/polar-regions/',
        },
        {
          label: 'High Latitude Rules',
          link: '/high-latitude/',
        },
        {
          label: 'Madhab',
          link: '/madhab/',
        },
        {
          label: 'Qibla Direction',
          link: '/qibla/',
        },
        {
          label: 'Sunnah Times',
          link: '/sunnah-times/',
        },
        {
          label: 'CLI Usage',
          link: '/cli/',
        },
        {
          label: 'Timezone Handling',
          link: '/timezone/',
        },
        {
          label: 'Errors',
          link: '/errors/',
        },
        {
          label: 'API Reference',
          link: '/api-reference/',
        },
        {
          label: 'Migration',
          link: '/migration/',
        },
        {
          label: 'Changelog',
          link: '/changelog/',
        },
        {
          label: 'Citations',
          link: '/citations/',
        },
      ],
      plugins: versionsConfig.versions.length
        ? [starlightVersions({ versions: versionsConfig.versions, current: { label: versionsConfig.latest.label } })]
        : [],
    }),
  ],
});
