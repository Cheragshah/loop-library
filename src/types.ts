export interface Loop {
  id: string;
  name: string;
  /** The /slash invocation, if any. */
  slash?: string;
  /** The complete loop prompt, ready to copy and repurpose. */
  command: string;
  what_it_does: string;
  category: string;
  author: string;
  source: string;
  source_url: string;
  tags: string[];
  votes: number;
  mentions: number;
  trending: number;
  first_seen: string;
  last_seen: string;
  published: string;
}

export type SortKey = "trending" | "votes" | "name" | "last_seen";
