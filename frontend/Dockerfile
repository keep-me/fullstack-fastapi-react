FROM node:20-alpine AS development
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]


FROM node:20-alpine AS builder
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts && npm cache clean --force
COPY . .
RUN npm run build


FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /var/log/nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/cache/nginx && \
    chmod -R 755 /var/cache/nginx

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]