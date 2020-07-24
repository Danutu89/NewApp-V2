const webpack = require('webpack')
const path = require('path')
const config = require('sapper/config/webpack.js')
const pkg = require('./package.json')

const mode = process.env.NODE_ENV
const dev = mode === 'development'

const alias = { svelte: path.resolve('node_modules', 'svelte') }
const extensions = ['.mjs', '.js', '.json', '.svelte', '.html']
const mainFields = ['svelte', 'module', 'browser', 'main']

const { preprocess } = require('./svelte.config')

module.exports = {
	client: {
		entry: config.client.entry(),
		output: config.client.output(),
		resolve: { alias, extensions, mainFields },
		module: {
			rules: [
				{
					test: /\.(svelte|html)$/,
					use: {
						loader: 'svelte-loader-hot',
						options: {
							preprocess,
							emitCss: false,
							dev,
							hydratable: true,
							hotReload: true,
							hotOptions: {
								// whether to preserve local state (i.e. any `let` variable) or
								// only public props (i.e. `export let ...`)
								noPreserveState: false,
								// optimistic will try to recover from runtime errors happening
								// during component init. This goes funky when your components are
								// not pure enough.
								optimistic: true,

								// See docs of svelte-loader-hot for all available options:
								//
								// https://github.com/rixo/svelte-loader-hot#usage
							}, // Default: false
						},
					},
				},
			],
		},
		mode,
		plugins: [
			// pending https://github.com/sveltejs/svelte/issues/2377
			// dev && new webpack.HotModuleReplacementPlugin(),
			new webpack.DefinePlugin({
				'process.browser': true,
				'process.env.NODE_ENV': JSON.stringify(mode),
			}),
			new webpack.HotModuleReplacementPlugin(),
		].filter(Boolean),
		devtool: dev && 'inline-source-map',
	},

	server: {
		entry: config.server.entry(),
		output: config.server.output(),
		target: 'node',
		resolve: { alias, extensions, mainFields },
		externals: Object.keys(pkg.dependencies).concat('encoding'),
		module: {
			rules: [
				{
					test: /\.(svelte|html)$/,
					use: {
						// you don't need svelte-loader-hot here, but it avoids having to
						// also install svelte-loader
						loader: 'svelte-loader-hot',
						options: {
							preprocess,
							css: false,
							generate: 'ssr',
							dev,
						},
					},
				},
			],
		},
		mode: process.env.NODE_ENV,
		performance: {
			hints: false, // it doesn't matter if server.js is large
		},
	},

	serviceworker: {
		entry: config.serviceworker.entry(),
		output: config.serviceworker.output(),
		mode: process.env.NODE_ENV,
	},
	externals: {
		moment: 'moment',
	},
}
