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
EXPOSE 8080
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]