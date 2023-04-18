FROM node:18-alpine as base
ENV PATH /app/node_modules/.bin:$PATH
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
########### development ##################
FROM base as dev
COPY --from=base /app/node_modules /app/node_modules
WORKDIR /app
EXPOSE 8080
CMD ["npm", "start"]
FROM base as build-stage
ARG API_URL
ENV VITE_API_URL=${API_URL}
COPY --from=base /app/node_modules /app/node_modules
WORKDIR /app
RUN npm run build
########### production ###################
FROM nginx:stable-alpine as prod
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]