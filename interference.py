import math,time
from PIL import Image, ImageDraw

def get_dist2D(a,b):
    x = a[0]-b[0]
    y = a[1]-b[1]
    return math.sqrt((x**2)+(y**2))
def compile(images):
    img = images[0]
    for i in images[1:]:
        img = Image.alpha_composite(img,i)
    return img
class colour:
    #colour ramp
    @staticmethod
    def get_rgb(n):
        return (
            int(colour.get_r(n)*255),
            int(colour.get_g(n)*255),
            int(colour.get_b(n)*255)
        )
    @staticmethod
    def get_r(n):
        if n>0:
            return 1.0
        else:
            return n+1
    @staticmethod
    def get_b(n):
        if n<0:
            return 1.0
        else:
            return 1-n
    @staticmethod
    def get_g(n):
        if n>=0:
            return 1-n
        else:
            return n+1
class wave:
    @staticmethod
    def get_Intensity(d, f, t, s, w):
        '''
        Get Wave Intensity

        :param d: distance
        :param f: frame rate
        :param t: time (frames)
        :param s: scale (pixels per meter)
        :param w: wavelength'''
        leading_edge = (t*s*w)/f
        if d>leading_edge:
            return 0
        else:
            return math.sin(
                (2*math.pi* ((f*d)-(t*s*w)))/(f*w*s)
            )
    @staticmethod
    def get_Peak(n,t,l,s,f):
        '''
            :param n: nth peak
            :param t: time(frames)
            :param l: lambda (wavelength)
            :param s: Scale (pixels per meter)
            :param f: frame rate '''
        return ((t-((n+0.75)*f))*l*s)/f
    @staticmethod
    def get_Trough(n,t,l,s,f):
        '''
            :param n: nth trough
            :param t: time(frames)
            :param l: lambda (wavelength)
            :param s: Scale (pixels per meter)
            :param f: frame rate '''
        return ((t-((n+0.25)*f))*l*s)/f

class handler:
    def __init__(self, sources=[], res=(0,0,), scale=1):
        '''
        :param sources: List of sources (class: source)
        :param res: Resolution
        :param scale: Pixel Scale/ pixels per metre'''
        self.sources = sources
        self.res = res
        self.scale = scale

    def render_img(self, time, frame_rate):
        img = Image.new('RGB', self.res)
        for x in range(self.res[0]):
            for y in range(self.res[1]):
                loc = (x,y,)
                i_total = 0
                for s in self.sources:
                    i_total += wave.get_Intensity(
                        get_dist2D(s.location, loc),
                        frame_rate,
                        time,
                        self.scale,
                        s.wavelength
                        )
                i_total = (i_total)/len(self.sources)
                img.putpixel((x,y,),colour.get_rgb(i_total))
        return img
    
    def render_animation(self, file, frames, frame_rate):
        for frame in range(frames[0],frames[1]):
            print(frame,end = '')
            out_img = self.render_img(frame, frame_rate)
            out_img.save('{}{}.png'.format(file,frame),format = 'PNG')
            print(': Saved')

    def render_contours(self, pOt, time, frame_rate):
        '''
        :param pOt: peak Or trough
        :param time: time (frames)
        '''
        rendered = []
        for s in self.sources:
            loc = s.location
            img_render = Image.new('RGBA', self.res)
            img_draw = ImageDraw.Draw(img_render, 'RGBA')
            i = 0
            while True:
                r = pOt(i, time, s.wavelength, self.scale, frame_rate)
                if r<0:
                    break
                else:
                    img_draw.ellipse((loc[0]-r, loc[1]-r, loc[0]+r, loc[1]+r),(0, 0, 0, 0),outline = 'white')
                i+=1
            del img_draw
            rendered.append(img_render)
        return compile(rendered)

    def animate_contours(self, file, frames, frame_rate):

        for frame in range(frames[0], frames[1]):
            print(frame, end='')

            out_t = self.render_contours(wave.get_Peak, frame, frame_rate)
            out_t.save('{}troughs{}.png'.format(file, frame), format = 'PNG')

            out_p = self.render_contours(wave.get_Trough, frame, frame_rate)
            out_p.save('{}peaks{}.png'.format(file, frame), format = 'PNG')

            print(': Saved')

class source:
    def __init__(self, location, wavelength, phase):
        self.location = location
        self.wavelength = wavelength
        #self.phase = phase

if __name__ == '__main__':
    res = (100,100,)
    s = [
        source((0,0,),1,0),
        source((100,100,),1,0),
        source((50,100,),1,0)
    ]
    universe = handler(s,res,5)
    
    universe.render_animation('test/image',(0,1000,),25)