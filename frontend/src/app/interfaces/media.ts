export interface Media {
    id: string;
    desc?: string;
    src_type: MediaSrcType;
    src: string;
    type: MediaType;
    user_id?: string;
    common?: boolean;
}

export enum MediaSrcType {
    'generic web URL',
    'internal S3 storage'
}

export enum MediaType {
    'static image',
    'animated image',
    'video',
    'stream'
}
