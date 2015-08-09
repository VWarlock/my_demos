/***************************************************************************
 *   Copyright (C) 2007 by Jarik   *
 *   n/a   *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program; if not, write to the                         *
 *   Free Software Foundation, Inc.,                                       *
 *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
 ***************************************************************************/
#include "SDL.h"
SDL_Event event;
int done;
int dummy(int w,int h);
int (*resize_callback)(int w,int h)=dummy;


void set_resize_callback(int (*callback)(int w,int h))
{
	resize_callback=callback;
}




char key_pressed (void)
{
  if (SDL_PollEvent (&event))
    {
      if (event.type == SDL_QUIT)
	{
	  done = 1;
	}
      if (event.type == SDL_KEYDOWN)
	{
	  if (event.key.keysym.sym == SDLK_ESCAPE)
	    {
	      done = 1;
	    }
	  return event.key.keysym.sym;
	}
	if (event.type == SDL_VIDEORESIZE)
	{
		/* handle resize event */
//    		surface = SDL_SetVideoMode( event.resize.w,event.resize.h, 0, videoFlags );
//   		if ( !surface )
//		{
//   			fprintf( stderr, "Could not get a surface af
//    			Quit( 1 );
//		}
    		resize_callback( event.resize.w, event.resize.h );
	} 
    }
return 0;
}
void
begin_listen_keys (void)
{
  done = 0;
}

char
esc_pressed (void)
{
  if (SDL_PollEvent (&event))
    {
      if (event.type == SDL_QUIT)
	{
	  done = 1;
	}
      if (event.type == SDL_KEYDOWN)
	{
	  if (event.key.keysym.sym == SDLK_ESCAPE)
	    {
	      done = 1;
	    }
	  //   return event.key.keysym.sym;
	}

    }
  return done;
}
