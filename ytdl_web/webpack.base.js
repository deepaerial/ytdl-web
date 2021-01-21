const path = require('path');
const dotenv = require('dotenv');
const webpack = require("webpack");
const HtmlWebpackPlugin = require('html-webpack-plugin');
const WorkboxPlugin = require('workbox-webpack-plugin');
const WebpackPwaManifest = require('webpack-pwa-manifest')


dotenv_parsed = dotenv.config().parsed

module.exports = {
    entry: path.resolve(__dirname, './src/index.js'),
    output: {
        path: path.resolve(__dirname, './dist/'),
        filename: 'app.js',
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                }
            },
            {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader'],
            },
        ]
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './public/index.html',
            filename: 'index.html',
            favicon: './public/favicon.ico'
        }),
        new webpack.DefinePlugin({
            API_URL: JSON.stringify(dotenv_parsed.API_URL)
        }),
        new WebpackPwaManifest({
            name: 'YTDL - Web video downloader',
            short_name: 'YTDL',
            description: 'My awesome Progressive Web App!',
            background_color: '#FFFFFF',
            icons: [
                {
                    src: path.resolve('public/android-chrome-192x192.png'),
                    sizes: [96, 128, 192, 256, 384, 512] // multiple sizes
                },
            ],
            display: "standalone"
        }),
        new WorkboxPlugin.GenerateSW({
            clientsClaim: true,
            skipWaiting: true,
            runtimeCaching: [{
                // Match any request that ends with .png, .jpg, .jpeg or .svg.
                urlPattern: /\.(?:png|jpg|jpeg|svg)$/,
                // Apply a cache-first strategy.
                handler: 'NetworkFirst',
                options: {
                    // Use a custom cache name.
                    cacheName: 'images',
                    expiration: {
                        maxEntries: 10,
                    },
                },
            }],
        }),
    ]
};