import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import tailwind from '@astrojs/tailwind';
import { visit } from 'unist-util-visit';

// Rehype plugin to prepend base URL to markdown image src attributes
// so images like /images/slug/file.png become /ZhichengAnimationHome/images/slug/file.png
function rehypeBaseImagePath(base) {
  return (tree) => {
    visit(tree, 'element', (node) => {
      if (node.tagName === 'img' && node.properties && node.properties.src) {
        const src = node.properties.src;
        // Only rewrite absolute paths (starting with /) that don't already include the base
        if (src.startsWith('/') && !src.startsWith(base + '/')) {
          node.properties.src = base + src;
        }
      }
    });
    return tree;
  };
}

// https://astro.build/config
export default defineConfig({
  site: 'https://zhichengzc.github.io',
  base: '/ZhichengAnimationHome',
  integrations: [mdx(), tailwind()],
  markdown: {
    shikiConfig: {
      themes: {
        light: 'github-light',
        dark: 'github-dark',
      },
      wrap: true,
    },
    rehypePlugins: [
      [rehypeBaseImagePath, '/ZhichengAnimationHome'],
    ],
  },
});
