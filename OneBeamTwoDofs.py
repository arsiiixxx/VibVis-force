'''
Designed to plot data of one cylinder with two dofs.
Users just need to instantiate this class,
thus avoiding interactions with more abstarct classes including
ForceData, ForceMode, ForceAnalysis, and ForceVisualization.
'''
import json
import logging
import numpy
from ForceData import ForceData
from Beam import Beam
from ForceAnalysis import ForceAnalysis
from ForceVisualization import ForceVisualization

#logging.basicConfig(level=logging.DEBUG)


class OneBeamTwoDofs:
    '''
    node_i from 1 to node_num
    '''

    def __init__(
            self,
            # for force_data
            force_filename,
            save_directory,
            filetypes,
            # for beam
            mass_ratio,
            top_tension,
            horizontal,
            tension_include_boyancy,
            length,
            diameter,
            bending_stiffness,
            fluid_density,
            fluid_velocity):
        time, inline_force, crossflow_force =\
            numpy.loadtxt(force_filename, unpack=True)

        self._fluid_density = fluid_density
        self._fluid_velocity = fluid_velocity

        self._inline_force_data = ForceData(
            time=time, force=inline_force)
        self._crossflow_force_data = ForceData(
            time=time, force=crossflow_force)
        self._beam = Beam(
            node_number=self._crossflow_force_data.node_number,
            mass_ratio=mass_ratio,
            top_tension=top_tension,
            horizontal=horizontal,
            tension_include_boyancy=tension_include_boyancy,
            length=length,
            diameter=diameter,
            bending_stiffness=bending_stiffness)
        self._save_directory = save_directory
        if self._save_directory[-1] != '/':
            self._save_directory += '/'

        self._filetypes = filetypes

        self._beam.plot_modal_shapes(
            self._append_filetypes('modal_shapes'), max_order=5)

        with open(self._save_directory + 'natural_frequencies.txt',
                  'wb') as file_:
            numpy.savetxt(
                file_, self._beam.natural_frequencies[:20], fmt='%.4e')

    def _append_filetypes(self, filename):
        return [
            self._save_directory + filename + '.' + filetype
            for filetype in self._filetypes
        ]

    # x
    def plot_inline_force(
            self,
            # for force_analysis
            start_time,
            end_time,
            medium_step,
            short_step,
            force_min,
            force_max,
            force_delta,
            force_std,
            curvature_min,
            curvature_max,
            curvature_delta,
            curvature_std,
            frequency_min,
            frequency_max,
            mode_number_min,
            mode_number_max,
            modal_weight_force_delta,
            make_animation=False,
            contour_curvature=False,
            wavelet_analysis=False):
        print('Starting inline plotting...')

        inline_force_analysis =\
                ForceAnalysis(
                        force_data=self._inline_force_data,
                        beam=self._beam,
                        fluid_density=self._fluid_density,
                        fluid_velocity=self._fluid_velocity,
                        start_time=start_time,
                        end_time=end_time,
                        frequency_min=frequency_min,
                        frequency_max=frequency_max,
                        mode_number_min=mode_number_min,
                        mode_number_max=mode_number_max,
                        modal_analysis=True,
                        wavelet_analysis=wavelet_analysis,
                        frequency_domain_analysis=True)
        inline_force_visulization = ForceVisualization(
            inline_force_analysis)

        start_time = inline_force_visulization.force_analysis.start_time
        end_time = inline_force_visulization.force_analysis.end_time

        inline_force_visulization.subplot_power_spectral_density(
            self._append_filetypes('inline_power_spectral_density_subplot'))
        inline_force_visulization.contourf_power_spectral_density(
            self._append_filetypes('inline_power_spectral_density_contourf'),
            contourf_num=51)
        inline_force_visulization.contour_power_spectral_density(
            self._append_filetypes('inline_power_spectral_density_contour'),
            contour_num=11)
        inline_force_visulization.subplot_modal_power_spectral_density(
            self._append_filetypes(
                'inline_modal_power_spectral_density_subplot'))
        inline_force_visulization.contourf_wavelet_dominant_frequency(
            self._append_filetypes(
                'inline_wavelet_dominant_frequency_contourf'),
            start_time=start_time,
            end_time=end_time,
            contourf_num=51)
        inline_force_visulization.contour_wavelet_dominant_frequency(
            self._append_filetypes(
                'inline_wavelet_dominant_frequency_contour'),
            start_time=start_time,
            end_time=end_time,
            contour_num=11)

        inline_force_visulization.subplot_wavelet_dominant_frequency(
            out_filenames=self._append_filetypes('inline_subplot_wavelet'),
            start_time=start_time,
            end_time=end_time,
            ymin=frequency_min,
            ymax=frequency_max,
            num=9)

        for node_i in range(
                10,
                inline_force_visulization.force_analysis.node_number,
                10):
            inline_force_visulization.contourf_wavelet(
                node_i,
                self._append_filetypes(
                    'inline_wavelet_contourf_node_{:d}'.format(node_i)),
                start_time=start_time,
                end_time=end_time,
                contourf_num=51)
            inline_force_visulization.contour_wavelet(
                node_i,
                self._append_filetypes(
                    'inline_wavelet_contour_node_{:d}'.format(node_i)),
                start_time=start_time,
                end_time=end_time,
                contour_num=11)
            inline_force_visulization.plot_wavelet_dominant_frequency(
                self._append_filetypes(
                    'inline_wavelet_dominant_frequency_node_{:d}'.format(
                        node_i)),
                node_i,
                start_time=start_time,
                end_time=end_time)

        inline_force_visulization.subplot_span_force(
            out_filenames=self._append_filetypes(
                'inline_subplot_force'),
            start_time=start_time,
            end_time=end_time,
            force_label=r'$x\cdot D^{-1}$',
            force_min=force_min,
            force_max=force_max)

        inline_force_visulization.subplot_span_force_deviation(
            out_filenames=self._append_filetypes(
                'inline_subplot_force_deviation'),
            start_time=start_time,
            end_time=end_time,
            force_deviation_label=r'$(x-\bar{x})\cdot D^{-1}$',
            force_deviation_min=-force_delta,
            force_deviation_max=force_delta)

        inline_force_visulization.subplot_modal_weight_force(
            out_filenames=self._append_filetypes('inline_mode'),
            start_time=start_time,
            end_time=end_time,
            ylabel=r'$u^m\cdot D^{-1}$',
            ymin=-modal_weight_force_delta,
            ymax=modal_weight_force_delta)

        inline_force_mean = inline_force_visulization.plot_force_mean(
            self._append_filetypes('inline_force_mean_{:.1f}_{:.1f}'.
                                   format(start_time, end_time)),
            xlabel=r'$x\cdot D^{-1}$',
            xmin=force_min,
            xmax=force_max, )
        with open(self._save_directory +
                  'inline_force_mean_{:.1f}_{:.1f}.txt'.format(
                      start_time, end_time), 'w') as outfile:
            json.dump(inline_force_mean, outfile)
        inline_curvature_mean = inline_force_visulization.plot_curvature_mean(
            self._append_filetypes('inline_curvature_mean_{:.1f}_{:.1f}'.
                                   format(start_time, end_time)),
            xlabel=r'$x\cdot D^{-1}$',
            xmin=curvature_min,
            xmax=curvature_max, )
        with open(self._save_directory +
                  'inline_curvature_mean_{:.1f}_{:.1f}.txt'.format(
                      start_time, end_time), 'w') as outfile:
            json.dump(inline_curvature_mean, outfile)
        inline_std = inline_force_visulization.plot_force_std(
            self._append_filetypes('inline_force_std_{:.1f}_{:.1f}'.
                                   format(start_time, end_time)),
            xlabel=r'$\sigma_x\cdot D^{-1}$',
            xmin=0,
            xmax=force_std, )
        numpy.savetxt(self._save_directory +
                      'inline_force_std_{:.1f}_{:.1f}.txt'.format(
                          start_time, end_time), inline_std)
        inline_std_curvature =\
            inline_force_visulization.plot_curvature_std(
                self._append_filetypes(
                    'inline_curvature_std_{:.1f}_{:.1f}'
                    .format(start_time, end_time)
                ),
                xlabel=r'$\sigma_{c_x}\cdot D$',
                xmin=0,
                xmax=curvature_std,
            )
        numpy.savetxt(self._save_directory +
                      'inline_curvature_std_{:.1f}_{:.1f}.txt'.format(
                          start_time, end_time), inline_std_curvature)

        inline_force_visulization.subplot_force_curvature_mean_std(
            self._append_filetypes(
                'inline_mean_std_force_curvature{:.1f}_{:.1f}'.format(
                    start_time, end_time)),
            xlabel_list=[
                r'$\bar{x}\cdot D^{-1}$', r'$\bar{c}_x\cdot D$',
                r'$\sigma_x\cdot D^{-1}$', r'$\sigma_{c_x}\cdot D$'
            ],
            xmin_list=[force_min, curvature_min, 0, 0],
            xmax_list=[
                force_max, curvature_max, force_std,
                curvature_std
            ], )

        # end_time += (-medium_step)
        end_time += -medium_step

        for time in numpy.arange(start_time, end_time, medium_step):
            inline_force_visulization.contourf_contour_spatio_temporal_force(
                self._append_filetypes(
                    'inline_spatio_temporal_force_{:.1f}'.format(time)),
                start_time=time,
                end_time=(time + medium_step),
                colorbar_min=-force_delta,
                colorbar_max=force_delta,
                contourf_num=51,
                contour_num=11,
                colorbar_zlabel=r'$x\cdot D^{-1}$')
            inline_force_visulization.contour_spatio_temporal_force(
                self._append_filetypes(
                    'inline_spatio_temporal_force_contour_{:.1f}'.
                    format(time)),
                start_time=time,
                end_time=(time + medium_step),
                colorbar_min=-force_delta,
                colorbar_max=force_delta,
                contour_num=11, )

        if contour_curvature:
            for time in numpy.arange(start_time, end_time, medium_step):
                inline_force_visulization.contourf_contour_spatio_temporal_curvature(
                    self._append_filetypes(
                        'inline_spatio_temporal_curvature_{:.1f}'.format(
                            time)),
                    start_time=time,
                    end_time=(time + medium_step),
                    colorbar_min=-curvature_delta,
                    colorbar_max=curvature_delta,
                    contourf_num=51,
                    contour_num=11,
                    colorbar_zlabel=r'$c_{x}\cdot D^{-1}$')
                inline_force_visulization.contour_spatio_temporal_curvature(
                    self._append_filetypes(
                        'inline_spatio_temporal_curvature_contour_{:.1f}'.
                        format(time)),
                    start_time=time,
                    end_time=(time + medium_step),
                    colorbar_min=-curvature_delta,
                    colorbar_max=curvature_delta,
                    contour_num=11)

        end_time += (medium_step - short_step)

        for time in numpy.arange(start_time, end_time, short_step):
            inline_force_visulization.plot_outline(
                self._append_filetypes('inline_outline_{:.1f}'.format(time)),
                xlabel=r'$x\cdot D^{-1}$',
                xmin=force_min,
                xmax=force_max,
                start_time=time,
                end_time=(time + short_step),
                line_number=25)
            inline_force_visulization.plot_deviation_outline(
                self._append_filetypes(
                    'inline_deviation_outline_{:.1f}'.format(time)),
                xlabel=r'$(x-\bar{x})\cdot D^{-1}$',
                xmin=-force_delta,
                xmax=force_delta,
                start_time=time,
                end_time=(time + short_step),
                line_number=25)

        with open(self._save_directory + 'inline_oscillatory_frequencies.txt',
                  'wb') as file_:
            numpy.savetxt(
                file_,
                inline_force_analysis.oscillatory_frequencies,
                fmt='%.4e')

        # animation
        if make_animation:
            inline_force_visulization.make_force_animation_along_time(
                [self._save_directory + 'inline_force_animation.gif'],
                start_time=start_time,
                end_time=end_time,
                xlabel=r'$x\cdot D^{-1}$',
                xmin=force_min,
                xmax=force_max)

        print('Inline plotting finished.')

    # y
    def plot_crossflow_force(
            self,
            # for force_analysis
            start_time,
            end_time,
            # ,
            medium_step,
            short_step,
            force_min,
            force_max,
            force_delta,
            force_std,
            curvature_min,
            curvature_max,
            curvature_delta,
            curvature_std,
            frequency_min,
            frequency_max,
            mode_number_min,
            mode_number_max,
            modal_weight_force_delta,
            make_animation=False,
            contour_curvature=False,
            wavelet_analysis=False):
        print('Starting crossflow plotting...')
        crossflow_force_analysis = ForceAnalysis(
            force_data=self._crossflow_force_data,
            beam=self._beam,
            fluid_density=self._fluid_density,
            fluid_velocity=self._fluid_velocity,
            start_time=start_time,
            end_time=end_time,
            frequency_min=frequency_min,
            frequency_max=frequency_max,
            mode_number_min=mode_number_min,
            mode_number_max=mode_number_max,
            modal_analysis=True,
            frequency_domain_analysis=True,
            wavelet_analysis=wavelet_analysis, )
        crossflow_force_visulization = ForceVisualization(
            crossflow_force_analysis)

        start_time = crossflow_force_visulization.force_analysis.start_time
        end_time = crossflow_force_visulization.force_analysis.end_time

        crossflow_force_visulization.subplot_power_spectral_density(
            self._append_filetypes('crossflow_power_spectral_density_subplot'))
        crossflow_force_visulization.subplot_modal_power_spectral_density(
            self._append_filetypes(
                'crossflow_modal_power_spectral_density_subplot'))
        crossflow_force_visulization.contourf_power_spectral_density(
            self._append_filetypes(
                'crossflow_power_spectral_density_contourf'),
            contourf_num=51)
        crossflow_force_visulization.contour_power_spectral_density(
            self._append_filetypes('crossflow_power_spectral_density_contour'),
            contour_num=11)
        crossflow_force_visulization.contourf_wavelet_dominant_frequency(
            self._append_filetypes(
                'crossflow_wavelet_dominant_frequency_contourf'),
            start_time=start_time,
            end_time=end_time,
            contourf_num=51)
        crossflow_force_visulization.contour_wavelet_dominant_frequency(
            self._append_filetypes(
                'crossflow_wavelet_dominant_frequency_contour'),
            start_time=start_time,
            end_time=end_time,
            contour_num=11)

        crossflow_force_visulization.subplot_wavelet_dominant_frequency(
            out_filenames=self._append_filetypes('crossflow_subplot_wavelet'),
            start_time=start_time,
            end_time=end_time,
            ymin=frequency_min,
            ymax=frequency_max,
            num=9)

        for node_i in range(10, crossflow_force_visulization.
                            force_analysis.node_number, 10):
            crossflow_force_visulization.contourf_wavelet(
                node_i,
                self._append_filetypes(
                    'crossflow_wavelet_contourf_node_{:d}'.format(node_i)),
                start_time=start_time,
                end_time=end_time,
                contourf_num=51)
            crossflow_force_visulization.contour_wavelet(
                node_i,
                self._append_filetypes(
                    'crossflow_wavelet_contour_node_{:d}'.format(node_i)),
                start_time=start_time,
                end_time=end_time,
                contour_num=11)
            crossflow_force_visulization.plot_wavelet_dominant_frequency(
                self._append_filetypes(
                    'crossflow_wavelet_dominant_frequency_node_{:d}'.format(
                        node_i)),
                node_i,
                start_time=start_time,
                end_time=end_time)

        crossflow_force_visulization.subplot_span_force(
            out_filenames=self._append_filetypes(
                'crossflow_subplot_force'),
            start_time=start_time,
            end_time=end_time,
            force_label=r'$y\cdot D^{-1}$',
            force_min=force_min,
            force_max=force_max)

        crossflow_force_visulization.subplot_span_force_deviation(
            out_filenames=self._append_filetypes(
                'crossflow_subplot_force_deviation'),
            start_time=start_time,
            end_time=end_time,
            force_deviation_label=r'$(y-\bar{y})\cdot D^{-1}$',
            force_deviation_min=-force_delta,
            force_deviation_max=force_delta)

        crossflow_force_visulization.subplot_modal_weight_force(
            out_filenames=self._append_filetypes('crossflow_mode'),
            start_time=start_time,
            end_time=end_time,
            ylabel=r'$v^m\cdot D^{-1}$',
            ymin=-modal_weight_force_delta,
            ymax=modal_weight_force_delta)

        crossflow_force_visulization.plot_force_mean(
            self._append_filetypes('crossflow_force_mean_{:.1f}_{:.1f}'.
                                   format(start_time, end_time)),
            xlabel=r'$y\cdot D^{-1}$',
            xmin=force_min,
            xmax=force_max, )
        crossflow_force_visulization.plot_curvature_mean(
            self._append_filetypes('crossflow_curvature_mean_{:.1f}_{:.1f}'.
                                   format(start_time, end_time)),
            xlabel=r'$y\cdot D^{-1}$',
            xmin=curvature_min,
            xmax=curvature_max, )
        crossflow_force_visulization.plot_force_std(
            self._append_filetypes('crossflow_force_std_{:.1f}_{:.1f}'.
                                   format(start_time, end_time)),
            xlabel=r'$\sigma_y\cdot D^{-1}$',
            xmin=0,
            xmax=force_std, )
        crossflow_force_visulization.plot_curvature_std(
            self._append_filetypes('crossflow_curvature_std_{:.1f}_{:.1f}'.
                                   format(start_time, end_time)),
            xlabel=r'$\sigma_{c_y}\cdot D$',
            xmin=0,
            xmax=curvature_std, )
        crossflow_force_visulization.subplot_force_curvature_std(
            self._append_filetypes(
                'crossflow_std_force_curvature{:.1f}_{:.1f}'.format(
                    start_time, end_time)),
            xlabel_list=[r'$\sigma_y\cdot D^{-1}$', r'$\sigma_{c_y}\cdot D$'],
            xmin_list=[0, 0],
            xmax_list=[force_std, curvature_std], )

        end_time += -medium_step

        for time in numpy.arange(start_time, end_time, medium_step):
            crossflow_force_visulization.contourf_contour_spatio_temporal_force(
                self._append_filetypes(
                    'crossflow_spatio_temporal_force_{:.1f}'.format(
                        time)),
                start_time=time,
                end_time=(time + medium_step),
                colorbar_min=-force_delta,
                colorbar_max=force_delta,
                contourf_num=51,
                contour_num=7,
                colorbar_zlabel=r'$y\cdot D^{-1}$')
            crossflow_force_visulization.contour_spatio_temporal_force(
                self._append_filetypes(
                    'crossflow_spatio_temporal_force_contour_{:.1f}'.
                    format(time)),
                start_time=time,
                end_time=(time + medium_step),
                colorbar_min=-force_delta,
                colorbar_max=force_delta,
                contour_num=7, )

        if contour_curvature:
            for time in numpy.arange(start_time, end_time, medium_step):
                crossflow_force_visulization.contourf_contour_spatio_temporal_curvature(
                    self._append_filetypes(
                        'crossflow_spatio_temporal_curvature_{:.1f}'.format(
                            time)),
                    start_time=time,
                    end_time=(time + medium_step),
                    colorbar_min=-curvature_delta,
                    colorbar_max=curvature_delta,
                    contourf_num=51,
                    contour_num=7,
                    colorbar_zlabel=r'$c_{y}\cdot D^{-1}$')
                crossflow_force_visulization.contour_spatio_temporal_curvature(
                    self._append_filetypes(
                        'crossflow_spatio_temporal_curvature_contour_{:.1f}'.
                        format(time)),
                    start_time=time,
                    end_time=(time + medium_step),
                    colorbar_min=-curvature_delta,
                    colorbar_max=curvature_delta,
                    contour_num=7)

        end_time += medium_step - short_step

        for time in numpy.arange(start_time, end_time, short_step):
            crossflow_force_visulization.plot_outline(
                self._append_filetypes('crossflow_outline_{:.1f}'.format(
                    time)),
                xlabel=r'$y\cdot D^{-1}$',
                xmin=force_min,
                xmax=force_max,
                start_time=time,
                end_time=(time + short_step),
                line_number=25)
            crossflow_force_visulization.plot_deviation_outline(
                self._append_filetypes(
                    'crossflow_deviation_outline_{:.1f}'.format(time)),
                xlabel=r'$(y-\bar{y})\cdot D^{-1}$',
                xmin=-force_delta,
                xmax=force_delta,
                start_time=time,
                end_time=(time + short_step),
                line_number=25)

        with open(
                self._save_directory + 'crossflow_oscillatory_frequencies.txt',
                'wb') as file_:
            numpy.savetxt(
                file_,
                crossflow_force_analysis.oscillatory_frequencies,
                fmt='%.4e')

        # animation
        if make_animation:
            crossflow_force_visulization.make_force_animation_along_time(
                [
                    self._save_directory +
                    'crossflow_force_animation.gif'
                ],
                start_time=start_time,
                end_time=end_time,
                xlabel=r'$y\cdot D^{-1}$',
                xmin=force_min,
                xmax=force_max)
        print('Crossflow plotting finished.')
