import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const category = searchParams.get('category') || 'business';
  const pageSize = searchParams.get('pageSize') || '5';
  
  const response = await fetch(
    `https://newsapi.org/v2/top-headlines?country=us&category=${category}&pageSize=${pageSize}&apiKey=${process.env.NEWS_API_KEY}`
  );
  const data = await response.json();
  return NextResponse.json(data);
}

export async function GET_science() {
  const response = await fetch(`https://newsapi.org/v2/top-headlines?country=us&category=science&apiKey=${process.env.NEWS_API_KEY}`);
  const data = await response.json();
  return NextResponse.json(data);
} 