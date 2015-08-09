#!/usr/bin/env python
# -*- encoding=UTF-8 -*-

import sys
import re


def search_mtl():
	global use_mtl
	global mtl_filename
	re_mtl=re.compile(r"^mtllib .*")
	mtl_l=[ s for s in lines if re_mtl.match(s)]
	if len(mtl_l)==0:
		use_mtl=0
		return
	use_mtl=1
	mtl_filename=re.sub(r"\n$","",re.sub("^mtllib ","",mtl_l[0]))
	print "using mtl : %s" % (mtl_filename)

def scan_values(pattern,source):
	txt=[ re.sub(r"\n$","",re.sub(pattern,"",s)) for s in source if re.match(pattern,s)]
	res=[ [ float(f) for f in re.split(r"\s+",s)] for s in txt]
	return res

def load_vertex():
	global vertex
	vertex=scan_values(r"^v\s",lines)
	print "%i verticies found" % (len(vertex))

def load_normals():
	global normals
	normals=scan_values(r"^vn\s",lines)
	print "%i normals found" % (len(normals))

def load_texcoord():
	global texcoords
	texcoords=scan_values(r"^vt\s",lines)
	print "%i texture coordinates found" % (len(texcoords))
	

# материал:
#   {  "<name>" :  [  index,
#					  [faceN,faceN,...],
#					  [Ns],
#					  [Ka r, g, b],
#					  [Kd r, g, b],
#					  [Ks r, g, b],
#					  [Ni],
#					  [d],
#					  [illum] ] }



def load_materials():
	global use_mtl
	global material
	material={}
	if use_mtl==0: return
	try:
		mtl_file=open(mtl_filename,"r")
	except IOError,err:
		print mtl_filename+" : ",
		print err.strerror
		use_mtl=0
		return
	mtl_lines=mtl_file.readlines()
	mtl_file.close()
	print "%s loaded" % (mtl_filename)
	mtl_line_index=[]
	for i in xrange(len(mtl_lines)):
		if re.match(r"^newmtl\s",mtl_lines[i]): mtl_line_index.append(i)
	mtl_txt=[]
	for i in xrange(len(mtl_line_index[:-1])):
		mtl_txt.append(mtl_lines[mtl_line_index[i]:mtl_line_index[i+1]])
	mtl_txt.append(mtl_lines[mtl_line_index[-1]:])
	print "%i materials found" % (len(mtl_txt))
	for i in xrange(len(mtl_txt)):
		mat=[i,[]]
		name=re.sub(r"\s$","",re.sub(r"^newmtl\s","",mtl_txt[i][0]))
		mat.append(scan_values(r"^Ns\s",mtl_txt[i])[0])
		mat.append(scan_values(r"^Ka\s",mtl_txt[i])[0])
		mat.append(scan_values(r"^Kd\s",mtl_txt[i])[0])
		mat.append(scan_values(r"^Ks\s",mtl_txt[i])[0])
		mat.append(scan_values(r"^Ni\s",mtl_txt[i])[0])
		mat.append(scan_values(r"^d\s",mtl_txt[i])[0])
		mat.append(scan_values(r"^illum\s",mtl_txt[i])[0])
		material[name]=mat

#	face   [ [ [ v , vt, vn] , [ ...], [ ...] ], ... ]

def	load_faces():
	global faces
	faces=[]
	re_face=re.compile(r"^f\s")
	re_mtl=re.compile(r"^usemtl\s")
	for i in xrange(len(lines)):
		if re_face.match(lines[i]):
			f_txt=re.sub(r"\s$","",re_face.sub("",lines[i]))
			f_v_txt=re.split(r"\s",f_txt)
			f_=[]
			for j in f_v_txt:
				f_v_=re.split(r"/",j)
				f_v=[]
				for k in f_v_:
					if k.isdigit():
						f_v.append(int(k))
					else:
						f_v.append(-1)
				f_.append(f_v)
			faces.append(f_)
		if re_mtl.match(lines[i]):
			mtl_name=re.sub(r"\s$","",re_mtl.sub("",lines[i]))
			material[mtl_name][1].append(len(faces))
	print "%i faces found" % (len(faces))


def parse_file():
	global lines
	try:
		obj_file = open(filename,"r")
	except IOError, err:
		print filename+" : ",
		print err.strerror
		quit()
	lines=obj_file.readlines()
	obj_file.close()
	print "%i lines readed from %s" % (len(lines),filename)
	search_mtl()
	load_vertex()
	load_normals()
	load_texcoord()
	load_materials()
	load_faces()

def write_c_header():
	res=[]
	res.append("// Generated by obj2c\n")
	res.append("#include <stdlib.h>\n")
	res.append("#include <GL/gl.h>\n")
	res.append("#include <stdint.h>\n")
	res.append("\n")
	res.append("typedef GLfloat point2[2];\n")
	res.append("typedef GLfloat point3[3];\n")
	res.append("typedef int16_t face_t[3][3];\n")
	res.append("typedef struct mtl_str\n")
	res.append("{\n")
	res.append("\tuint32_t index;\n")
	res.append("\tGLfloat Ns;\n")
	res.append("\tGLfloat Ka[3];\n")
	res.append("\tGLfloat Ka_alpha;\n")
	res.append("\tGLfloat Kd[3];\n")
	res.append("\tGLfloat Kd_alpha;\n")
	res.append("\tGLfloat Ks[3];\n")
	res.append("\tGLfloat Ks_alpha;\n")
	res.append("\tGLfloat Ni;\n")
	res.append("\tGLfloat d;\n")
	res.append("\tGLfloat illum;\n")
	res.append("\tuint16_t start_faces_length;\n")
	res.append("\tuint16_t *start_faces;\n")
	res.append("} mtl_t;\n")
	res.append("\n\n")
	return res


def write_list(list_):
	res=[]
	for i in xrange(len(list_)):
		s="\t{ "
		for j in xrange(len(list_[i])):
			s+=str(list_[i][j])
			if j<(len(list_[i])-1): s+=","
		s+="}"
		if i<(len(list_)-1): s+=","
		res.append(s+"\n")
	return res


def write_c_values(type,name,list_):
	res=[]
	res.append("uint32_t Num_"+base_name+"_"+name+"="+str(len(list_))+";\n")
	res.append("\n")
	res.append(type+"\t"+ base_name + "_"+name+"[]= { " +"\n")
	res+=write_list(list_)
	res.append("};\n\n")
	return res
	
def write_c_faces():
	res=[]
	name="faces"
	list_=faces
	type="face_t"
	res.append("uint32_t Num_"+base_name+"_"+name+"="+str(len(list_))+";\n")
	res.append("\n")
	res.append("//	face   [ [ [ v , vt, vn] , [ ...], [ ...] ], ... ]\n\n")
	res.append(type+"\t"+ base_name + "_"+name+"[]= { " +"\n")
	for i in xrange(len(list_)):
		s="\t{ "
		for j in xrange(len(list_[i])):
			s+="{ "
			for k in xrange(len(list_[i][j])):
				s+=str(list_[i][j][k])
				if k<(len(list_[i][j])-1): s+=","
			s+="}"
			if j<(len(list_[i])-1): s+=","
		s+="}"
		if i<(len(list_)-1): s+=","
		res.append(s+"\n")
	res.append("};\n\n")
	return res



def write_lines(lines):
	try:
		c_file.writelines(lines)
	except IOError, err:
		print c_filename+" : ",
		print err.strerror
		quit()
	
def write_c_color(clr):
	s="{"
	for i in xrange(len(clr)):
		s+=str(clr[i])
		if i<len(clr)-1: s+=","
	s+="}"
	return s

def write_c_materials():
	res=[]
	res1=[]
	res3=[]
	res.append("uint32_t Num_"+base_name+"_materials="+str(len(material))+";\n\n")
	res.append("mtl_t "+base_name+"_materials[]= \n{\n")
	res3.append("void "+base_name+"_materials_init()\n{\n")
	for i in material.keys():
		m=material[i]
		s="\t{"
		s+=str(m[0])+","+str(m[2][0])
		s+=","+write_c_color(m[3])+",1.0"
		s+=","+write_c_color(m[4])+",1.0"
		s+=","+write_c_color(m[5])+",1.0"
		s+=","+str(m[6][0])+","+str(m[7][0])
		s+=","+str(m[8][0])
		s+=","+str(len(m[1]))
		s+=", NULL"
		s+="}"
		if i!=material.keys()[-1]: s+=","
		res.append(s+"\n")
		mn=re.sub(r"\.","_",i)
		res1.append("uint16_t "+base_name+"_"+mn+"_faces[]= "+write_c_color(m[1])+";\n")
		res3.append("\t"+base_name+"_materials["+str(material.keys().index(i))+"].start_faces="+base_name+"_"+mn+"_faces;\n")
	res.append("};\n\n")
	res1.append("\n\n")
	res3.append("}\n\n")
	res+=res1
	res+=res3
	return res

def write_c_code():
	res=[]
	s="\n// code\n\n"
	s+="void %s_bind_texture(uint16_t mat)\n" % (base_name)
	s+="{\n"
	for i in xrange(len(material.keys())):
		s=s+"\tif(mat==%(index)s)\n\t{\n\t\t//bind texture for material %(name)s\n\t\treturn;\n\t}\n" %{"index":str(i),"name":material.keys()[i]}
	s+="}\n\n"
	s+="void %s_check_material(uint16_t face)\n" % (base_name)
	s+="{\n"
	s+="\tuint16_t mat,i,n_faces;\n\tchar flg;\n\tGLfloat params[4];\n\n"
	s+="\tfor(mat=0;mat<Num_%s_materials;mat++)\n" % (base_name)
	s+="\t{\n"
	s+="\t\tn_faces=%s_materials[mat].start_faces_length;\n" % (base_name)
	s+="\t\tflg=0;\n"
	s+="\t\tif(n_faces)\n"
	s+="\t\t{\n"
	s+="\t\t\tfor(i=0;i<n_faces;i++)\n"
	s+="\t\t\t{\n"
	s+="\t\t\t\tif(%s_materials[mat].start_faces[i]==face) flg=1;\n" % (base_name)
	s+="\t\t\t}\n"
	s+="\t\t}\n"
	s+="\t\tif(flg)    // Select material\n"
	s+="\t\t{\n"
	s+="\t\t\tparams[0]=%s_materials[mat].Ka[0];\n" % (base_name)
	s+="\t\t\tparams[1]=%s_materials[mat].Ka[1];\n" % (base_name)
	s+="\t\t\tparams[2]=%s_materials[mat].Ka[2];\n" % (base_name)
	s+="\t\t\tparams[3]=%s_materials[mat].Ka_alpha;\n" % (base_name)
	s+="\t\t\tglMaterialfv (GL_FRONT_AND_BACK,GL_AMBIENT,params);\n"
	s+="\t\t\tparams[0]=%s_materials[mat].Kd[0];\n" % (base_name)
	s+="\t\t\tparams[1]=%s_materials[mat].Kd[1];\n" % (base_name)
	s+="\t\t\tparams[2]=%s_materials[mat].Kd[2];\n" % (base_name)
	s+="\t\t\tparams[3]=%s_materials[mat].Kd_alpha;\n" % (base_name)
	s+="\t\t\tglMaterialfv (GL_FRONT_AND_BACK,GL_DIFFUSE,params);\n"
	s+="\t\t\tparams[0]=%s_materials[mat].Ks[0];\n" % (base_name)
	s+="\t\t\tparams[1]=%s_materials[mat].Ks[1];\n" % (base_name)
	s+="\t\t\tparams[2]=%s_materials[mat].Ks[2];\n" % (base_name)
	s+="\t\t\tparams[3]=%s_materials[mat].Ks_alpha;\n" % (base_name)
	s+="\t\t\tglMaterialfv (GL_FRONT_AND_BACK,GL_SPECULAR,params);\n"
	s+="\t\t\tglMaterialf (GL_FRONT_AND_BACK,GL_SHININESS,%s_materials[mat].Ns);\n" % (base_name)
	s+="\t\t\t%s_bind_texture(mat);\n" % (base_name)
	s+="\t\t}\n"
	s+="\t}\n"
	s+="}\n\n"
	s+="GLint %s_generate_list()\n" % (base_name)
	s+="{\n"
	s+="\tuint16_t i,j;\n"
	s+="\tint32_t ind;\n"
	s+="\tGLint list;\n\n"
	s+="\t%s_materials_init();\n" % (base_name)
	s+="\tlist=glGenLists(1);\n"
	s+="\tglNewList(list,GL_COMPILE);\n"
	s+="\tfor(i=0;i<Num_%s_faces;i++)\n" % (base_name)
	s+="\t{\n"
	s+="\t%s_check_material(i);\n" % (base_name)
	s+="\tglBegin(GL_TRIANGLES);\n"
	s+="\t\tfor(j=0;j<3;j++)\n"
	s+="\t\t{\n"
	s+="\t\t\tind=%s_faces[i][j][1]-1;\n" % (base_name)
	s+="\t\t\tif(ind>0)glTexCoord2f(%(n)s_texcoords[ind][0],%(n)s_texcoords[ind][1]);\n" % {"n":base_name}
	s+="\t\t\tind=%s_faces[i][j][2]-1;\n" % (base_name)
	s+="\t\t\tglNormal3f(%(n)s_normals[ind][0],%(n)s_normals[ind][1],%(n)s_normals[ind][2]);\n" % {"n":base_name}
	s+="\t\t\tind=%s_faces[i][j][0]-1;\n" % (base_name)
	s+="\t\t\tglVertex3f(%(n)s_vertex[ind][0],%(n)s_vertex[ind][1],%(n)s_vertex[ind][2]);\n" % {"n":base_name}
	s+="\t\t}\n"
	s+="\t\tglEnd();\n"
	s+="\t}\n"
	s+="\tglEndList();\n"
	s+="\treturn list;\n"
	s+="}\n"
	res.append(s)
	return res

def write_c_file():
	global c_file
	global base_name
	base_name=re.sub(r".[oO][bB][jJ]$","",filename)
	c_filename=base_name+".c"
	try:
		c_file = open(c_filename,"w")
	except IOError, err:
		print c_filename+" : ",
		print err.strerror
		quit()
	write_lines(write_c_header())
	write_lines(write_c_values("point3","vertex",vertex))
	write_lines(write_c_values("point3","normals",normals))
	write_lines(write_c_values("point2","texcoords",texcoords))
	write_lines(write_c_faces())
	write_lines(write_c_materials())
	write_lines(write_c_code())
	c_file.close()

def write_h_file():
	h_filename=base_name+".h"
	try:
		h_file = open(h_filename,"w")
	except IOError, err:
		print h_filename+" : ",
		print err.strerror
		quit()
	s="#include <GL/gl.h>\n"
	s+="GLint %s_generate_list();\n" % (base_name)
	h_file.writelines([s])
	h_file.close()

def main():
	args=sys.argv
	if len(args)<2:
		print "Usage: obj2c.py <filename.obj>"
		return 0
	global filename
	filename=args[1]
	parse_file()
	write_c_file()
	write_h_file()

	

if __name__ == "__main__":
    main()