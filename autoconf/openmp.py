#!/usr/bin/env python
# encoding: utf-8

from waflib.Configure import conf, ConfigurationError

OPENMP_CODE = '''
#ifndef _OPENMP
 choke me
#endif
#include <omp.h>
int main () { return omp_get_num_threads (); }
'''

@conf
def check_openmp_cflags(self, **kw):
    self.start_msg('Checking for $CC option to support OpenMP')
    kw.update({'fragment': OPENMP_CODE})
    try:
        self.validate_c(kw)
        self.run_c_code(**kw)
        if 'define_name' in kw:
            self.define(kw['define_name'], 1)
        self.end_msg('None')
    except ConfigurationError:
        for flag in ('-fopenmp', '-xopenmp', '-openmp', '-mp', '-omp', '-qsmp=omp'):
            try:
                self.validate_c(kw) #refresh env
                if kw['compiler'] == 'c':
                    kw['ccflags'] = kw['cflags'] = flag
                elif kw['compiler'] == 'cxx':
                    kw['cxxflags'] = flag
                else:
                    self.fatal('Compiler has to be "c" or "cxx"')
                kw['linkflags'] = flag
                kw['success'] = self.run_c_code(**kw)
                self.post_check(**kw)
                self.end_msg(flag)
                return
            except ConfigurationError:
		del kw['env']
                continue

        self.end_msg('Not supported')
        if 'define_name' in kw:
            self.undefine(kw['define_name'])
        if kw.get('mandatory', True):
            self.fatal('OpenMP is not supported')
