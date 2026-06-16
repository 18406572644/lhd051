FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/node:20-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci --registry=https://registry.npmmirror.com
COPY . .
RUN npm run build

FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/nginx:alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 2051
CMD ["nginx", "-g", "daemon off;"]
